from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
import logging

from ....database import get_db, CheckBatch, PreCheck, PostCheck
from ....models.schemas import BatchStatusResponse

router = APIRouter()

# Get logger instead of configuring it
logger = logging.getLogger(__name__)

@router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse, status_code=200)
async def get_batch_status(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get status of a batch check operation."""
    try:
        # Get the batch
        batch_stmt = select(CheckBatch).filter(CheckBatch.batch_id == str(batch_id))
        batch_result = await db.execute(batch_stmt)
        batch = batch_result.scalar_one_or_none()
        
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Get the prechecks associated with this batch
        precheck_stmt = select(PreCheck).filter(PreCheck.batch_id == str(batch_id))
        precheck_result = await db.execute(precheck_stmt)
        prechecks = precheck_result.scalars().all()
        
        if not prechecks:
            return {
                "batch_id": batch_id,
                "total_devices": batch.total_devices,
                "completed_devices": 0,
                "status": "initiated",
                "devices": []
            }
        
        devices = []
        completed_count = 0
        
        for precheck in prechecks:
            # Get the corresponding postcheck, if it exists
            postcheck_stmt = select(PostCheck).filter(PostCheck.precheck_id == precheck.id)
            postcheck_result = await db.execute(postcheck_stmt)
            postcheck = postcheck_result.scalar_one_or_none()
            
            # Calculate overall status and progress
            status = "in_progress"
            progress = 50  # Default to 50% if only precheck is done
            status_detail = "precheck_completed"
            
            if precheck.status == "failed":
                status = "failed"
                progress = 0
                status_detail = "precheck_failed"
            elif postcheck:
                if postcheck.status == "completed":
                    status = "completed"
                    progress = 100
                    status_detail = "postcheck_completed"
                    completed_count += 1
                elif postcheck.status == "failed":
                    status = "failed"
                    progress = 75  # Changed from 50 to 75 to indicate postcheck was attempted
                    status_detail = "postcheck_failed"
                else:
                    status = "in_progress"
                    progress = 75
                    status_detail = "postcheck_in_progress"
            
            devices.append({
                "device_ip": precheck.device_ip,
                "precheck_id": precheck.id,
                "postcheck_id": postcheck.id if postcheck else None,
                "status": status,
                "status_detail": status_detail,
                "progress": progress
            })
        
        # Determine overall batch status
        overall_status = batch.status
        if overall_status not in ["completed", "failed", "partial"]:
            # Recalculate status if it's not finalized
            if any(device["status"] == "failed" for device in devices):
                overall_status = "failed"
            elif all(device["status"] == "completed" for device in devices):
                overall_status = "completed"
            elif any(device["status"] == "in_progress" for device in devices):
                overall_status = "in_progress"
            else:
                overall_status = "partial"
        
        return {
            "batch_id": batch_id,
            "total_devices": batch.total_devices,
            "completed_devices": completed_count,
            "status": overall_status,
            "devices": devices
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error in get_batch_status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch status: {str(e)}"
        ) 