from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
import logging

from ....database import get_db, PreCheck, PostCheck, CheckBatch
from ....models.schemas import DiffResponse
from ....utils.diff_utils import generate_diff

router = APIRouter()

# Get logger instead of configuring it
logger = logging.getLogger(__name__)

@router.get("/batch/{batch_id}/diff", response_model=DiffResponse, status_code=200)
async def get_diff(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get differences between pre and post-change checks.
    
    Returns:
        200: Diff successfully generated
        404: Checks not found
        500: Internal server error
    """
    try:
        logger.info(f"Getting diff for batch: {batch_id}")
        
        # First get the batch
        batch_stmt = select(CheckBatch).filter(CheckBatch.batch_id == str(batch_id))
        batch_result = await db.execute(batch_stmt)
        batch = batch_result.scalar_one_or_none()
        
        if not batch:
            logger.warning(f"Batch not found: {batch_id}")
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Get prechecks associated with this batch
        precheck_stmt = select(PreCheck).filter(PreCheck.batch_id == str(batch_id))
        precheck_result = await db.execute(precheck_stmt)
        prechecks = precheck_result.scalars().all()
        
        if not prechecks:
            logger.warning(f"No prechecks found for batch: {batch_id}")
            raise HTTPException(status_code=404, detail="No prechecks found for this batch")
        
        logger.info(f"Found {len(prechecks)} prechecks for batch: {batch_id}")
        
        devices = []
        overall_status = "completed"
        
        for precheck in prechecks:
            # Get associated postcheck
            postcheck_stmt = select(PostCheck).filter(PostCheck.precheck_id == precheck.id)
            postcheck_result = await db.execute(postcheck_stmt)
            postcheck = postcheck_result.scalar_one_or_none()
            
            if not postcheck:
                logger.info(f"No postcheck found for precheck: {precheck.id}, device: {precheck.device_ip}")
                continue  # Skip if no postcheck for this precheck
            
            try:
                logger.info(f"Generating diff for device: {precheck.device_ip}, precheck: {precheck.id}, postcheck: {postcheck.id}")
                
                diff_result = await generate_diff(
                    precheck_id=precheck.id,
                    postcheck_id=postcheck.id,
                    device_ip=precheck.device_ip,
                    db=db
                )
                
                devices.append({
                    "device_ip": precheck.device_ip,
                    "precheck_id": precheck.id,
                    "postcheck_id": postcheck.id,
                    "status": diff_result["status"],
                    "summary": {
                        "total_commands": diff_result["total_commands"],
                        "commands_with_changes": diff_result["changes"],
                        "timestamp": datetime.utcnow()
                    }
                })
                
                logger.info(f"Diff generated for device: {precheck.device_ip}, changes: {diff_result['changes']}/{diff_result['total_commands']} commands")
                
                if diff_result["status"] != "completed":
                    overall_status = "partial"
                    logger.warning(f"Diff generation not completed for device: {precheck.device_ip}")
            except Exception as e:
                overall_status = "partial"
                logger.exception(f"Error generating diff for device: {precheck.device_ip}, error: {str(e)}")
        
        if not devices:
            logger.warning(f"No completed postcheck data found for diff generation, batch: {batch_id}")
            raise HTTPException(status_code=404, detail="No completed postcheck data found for diff generation")
        
        logger.info(f"Returning diff results for batch: {batch_id}, overall status: {overall_status}, devices: {len(devices)}")
            
        return {
            "batch_id": batch_id,
            "devices": devices,
            "overall_status": overall_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to generate diff for batch: {batch_id}, error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diff: {str(e)}"
        ) 