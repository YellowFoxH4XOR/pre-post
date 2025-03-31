from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func

from ....database import get_db, CheckBatch
from ....models.schemas import BatchStatusResponse, CheckListResponse

router = APIRouter()

@router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse, status_code=200)
async def get_batch_status(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get status of a batch check operation.
    
    Returns:
        200: Status successfully retrieved
        404: Batch not found
        500: Internal server error
    """
    try:
        stmt = select(CheckBatch).filter(CheckBatch.batch_id == str(batch_id))
        result = await db.execute(stmt)
        batch = result.scalar_one_or_none()
        
        if not batch:
            raise HTTPException(
                status_code=404,
                detail="Batch not found"
            )
        
        devices = []
        for device in batch.devices:
            devices.append({
                "device_ip": device.device_ip,
                "precheck_id": device.precheck_id,
                "postcheck_id": device.postcheck_id,
                "status": device.status,
                "progress": device.progress
            })
        
        return {
            "batch_id": batch_id,
            "total_devices": batch.total_devices,
            "completed_devices": batch.completed_devices,
            "status": batch.status,
            "devices": devices
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch status: {str(e)}"
        )

@router.get("/checks", response_model=CheckListResponse, status_code=200)
async def list_checks(
    device_ip: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    batch_id: Optional[UUID] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """List and filter check operations.
    
    Returns:
        200: Checks successfully retrieved
        400: Invalid query parameters
        500: Internal server error
    """
    try:
        if page < 1:
            raise HTTPException(
                status_code=400,
                detail="Page number must be greater than 0"
            )
        
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=400,
                detail="Page size must be between 1 and 100"
            )
            
        stmt = select(CheckBatch)
        
        if device_ip:
            stmt = stmt.filter(CheckBatch.devices.any(device_ip=device_ip))
        if status:
            stmt = stmt.filter(CheckBatch.status == status)
        if date_from:
            stmt = stmt.filter(CheckBatch.created_at >= date_from)
        if date_to:
            stmt = stmt.filter(CheckBatch.created_at <= date_to)
        if batch_id:
            stmt = stmt.filter(CheckBatch.batch_id == str(batch_id))
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = await db.scalar(count_stmt)
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(stmt)
        checks = result.scalars().all()
        
        return {
            "checks": [
                {
                    "check_id": check.id,
                    "batch_id": check.batch_id,
                    "type": check.type,
                    "device_ip": check.device_ip,
                    "status": check.status,
                    "timestamp": check.created_at
                }
                for check in checks
            ],
            "total": total,
            "page": page
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list checks: {str(e)}"
        ) 