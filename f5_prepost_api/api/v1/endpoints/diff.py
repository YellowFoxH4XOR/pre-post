from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
from datetime import datetime
from sqlalchemy import select

from ....database import get_db, PreCheck, PostCheck
from ....models.schemas import DiffResponse
from ....utils.diff_utils import generate_diff

router = APIRouter()

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
        # Update to use select with filter
        pre_stmt = select(PreCheck).filter(PreCheck.id == str(batch_id))
        post_stmt = select(PostCheck).filter(PostCheck.precheck_id == str(batch_id))
        
        pre_result = await db.execute(pre_stmt)
        post_result = await db.execute(post_stmt)
        
        precheck = pre_result.scalar_one_or_none()
        postcheck = post_result.scalar_one_or_none()
        
        if not precheck or not postcheck:
            raise HTTPException(
                status_code=404,
                detail="Checks not found"
            )
        
        devices = []
        overall_status = "completed"
        
        for device in precheck.devices:
            try:
                diff_result = await generate_diff(
                    precheck_id=str(batch_id),
                    postcheck_id=str(postcheck.id),
                    device_ip=device.device_ip,
                    db=db
                )
                
                devices.append({
                    "device_ip": device.device_ip,
                    "precheck_id": batch_id,
                    "postcheck_id": postcheck.id,
                    "status": diff_result["status"],
                    "summary": {
                        "total_commands": diff_result["total_commands"],
                        "commands_with_changes": diff_result["changes"],
                        "timestamp": datetime.utcnow()
                    }
                })
                
                if diff_result["status"] != "completed":
                    overall_status = "partial"
            except Exception:
                overall_status = "partial"
                
        return {
            "batch_id": batch_id,
            "devices": devices,
            "overall_status": overall_status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diff: {str(e)}"
        ) 