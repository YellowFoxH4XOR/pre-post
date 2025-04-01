from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List
import logging

from ....database import get_db, CheckBatch, PreCheck, PostCheck, PreCheckOutput, PostCheckOutput
from ....utils.diff_utils import generate_diff

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

@router.get("/batch/{batch_id}/diff")
async def get_diff(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get diff between pre and post check.
    
    Args:
        batch_id: Batch ID
        
    Returns:
        200: Diff data
        404: Batch not found
        500: Error generating diff
    """
    try:
        logger.info(f"Generating diff for batch_id: {batch_id}")
        
        # Get batch
        stmt = select(CheckBatch).filter(CheckBatch.batch_id == batch_id)
        result = await db.execute(stmt)
        batch = result.scalars().first()
        
        if not batch:
            logger.error(f"Batch not found: {batch_id}")
            raise HTTPException(status_code=404, detail=f"Batch not found: {batch_id}")
        
        # Get all prechecks for this batch
        stmt = select(PreCheck).filter(PreCheck.batch_id == batch_id)
        result = await db.execute(stmt)
        prechecks = result.scalars().all()
        
        if not prechecks:
            logger.warning(f"No prechecks found for batch: {batch_id}")
            raise HTTPException(status_code=404, detail=f"No prechecks found for batch: {batch_id}")
        
        # Process each precheck to get diff
        devices_result = []
        
        for precheck in prechecks:
            # Get postcheck for this precheck
            stmt = select(PostCheck).filter(PostCheck.precheck_id == precheck.id)
            result = await db.execute(stmt)
            postcheck = result.scalars().first()
            
            if not postcheck:
                logger.warning(f"No postcheck found for precheck: {precheck.id}")
                devices_result.append({
                    "device_ip": precheck.device_ip,
                    "precheck_id": str(precheck.id),
                    "postcheck_id": None,
                    "status": "pending",
                    "summary": None,
                    "all_commands": []
                })
                continue
            
            # Generate diff
            diff_data = await generate_diff(precheck.id, postcheck.id, precheck.device_ip, db)
            
            # Get all commands and their outputs
            all_commands = []
            
            # Get all precheck outputs
            stmt = select(PreCheckOutput).filter(PreCheckOutput.precheck_id == precheck.id)
            result = await db.execute(stmt)
            pre_outputs = result.scalars().all()
            
            # Get all postcheck outputs
            stmt = select(PostCheckOutput).filter(PostCheckOutput.postcheck_id == postcheck.id)
            result = await db.execute(stmt)
            post_outputs = result.scalars().all()
            
            # Create mapping of command to outputs
            pre_map = {po.command: po.output for po in pre_outputs}
            post_map = {po.command: po.output for po in post_outputs}
            
            # Process all commands
            for command in precheck.meta_data.get("commands", []):
                has_changes = command in diff_data.get("diffs", {})
                cmd_diff = diff_data.get("diffs", {}).get(command, []) if has_changes else []
                
                all_commands.append({
                    "command": command,
                    "has_changes": has_changes,
                    "diff": cmd_diff,
                    "pre_output": pre_map.get(command, ""),
                    "post_output": post_map.get(command, "")
                })
            
            devices_result.append({
                "device_ip": precheck.device_ip,
                "precheck_id": str(precheck.id),
                "postcheck_id": str(postcheck.id),
                "status": diff_data.get("status", "unknown"),
                "summary": {
                    "total_commands": diff_data.get("total_commands", 0),
                    "commands_with_changes": diff_data.get("changes", 0),
                    "timestamp": postcheck.timestamp,
                    "diff": diff_data.get("diffs", {})
                },
                "all_commands": all_commands
            })
        
        # Calculate overall status
        all_completed = all(device["status"] == "completed" for device in devices_result)
        any_pending = any(device["status"] == "pending" for device in devices_result)
        
        if any_pending:
            overall_status = "in_progress"
        elif all_completed:
            overall_status = "completed"
        else:
            overall_status = "partial"
        
        return {
            "batch_id": batch_id,
            "devices": devices_result,
            "overall_status": overall_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating diff: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate diff: {str(e)}"
        ) 