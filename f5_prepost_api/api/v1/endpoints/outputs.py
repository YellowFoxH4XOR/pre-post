from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict
import logging

from ....database import get_db, CheckBatch, PreCheck, PostCheck, PreCheckOutput, PostCheckOutput
from ....models.schemas import BatchOutputResponse

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

@router.get("/batch/{batch_id}/outputs", response_model=BatchOutputResponse)
async def get_batch_outputs(
    batch_id: str,
    device_ip: Optional[str] = Query(None, description="Filter outputs by device IP"),
    command: Optional[str] = Query(None, description="Filter outputs by command"),
    db: AsyncSession = Depends(get_db)
):
    """Get precheck and postcheck outputs for a batch.
    
    Args:
        batch_id: Batch ID to get outputs for
        device_ip: Optional filter by device IP
        command: Optional filter by command
        db: Database session
        
    Returns:
        200: Batch outputs
        404: Batch not found
        500: Internal server error
    """
    try:
        logger.info(f"Getting outputs for batch_id: {batch_id}")
        
        # Verify batch exists
        batch_query = select(CheckBatch).filter(CheckBatch.batch_id == batch_id)
        batch_result = await db.execute(batch_query)
        batch = batch_result.scalars().first()
        
        if not batch:
            logger.error(f"Batch not found: {batch_id}")
            raise HTTPException(status_code=404, detail=f"Batch not found: {batch_id}")
        
        # Get all prechecks for this batch
        precheck_query = select(PreCheck).filter(PreCheck.batch_id == batch_id)
        if device_ip:
            precheck_query = precheck_query.filter(PreCheck.device_ip == device_ip)
        precheck_result = await db.execute(precheck_query)
        prechecks = precheck_result.scalars().all()
        
        devices_output = []
        
        # Process each precheck
        for precheck in prechecks:
            # Get precheck outputs
            precheck_output_query = select(PreCheckOutput).filter(PreCheckOutput.precheck_id == precheck.id)
            if command:
                precheck_output_query = precheck_output_query.filter(PreCheckOutput.command == command)
            precheck_output_result = await db.execute(precheck_output_query)
            precheck_outputs = precheck_output_result.scalars().all()
            
            # Get postcheck for this precheck
            postcheck_query = select(PostCheck).filter(PostCheck.precheck_id == precheck.id)
            postcheck_result = await db.execute(postcheck_query)
            postcheck = postcheck_result.scalars().first()
            
            postcheck_outputs = []
            if postcheck:
                # Get postcheck outputs
                postcheck_output_query = select(PostCheckOutput).filter(PostCheckOutput.postcheck_id == postcheck.id)
                if command:
                    postcheck_output_query = postcheck_output_query.filter(PostCheckOutput.command == command)
                postcheck_output_result = await db.execute(postcheck_output_query)
                postcheck_outputs = postcheck_output_result.scalars().all()
            
            # Organize command outputs
            commands_output = []
            
            # Create a map of all commands
            command_map = {}
            
            # Add precheck commands
            for po in precheck_outputs:
                if po.command not in command_map:
                    command_map[po.command] = {
                        "command": po.command,
                        "pre_output": po.output,
                        "post_output": None,
                        "has_postcheck": False
                    }
                else:
                    command_map[po.command]["pre_output"] = po.output
            
            # Add postcheck commands
            for po in postcheck_outputs:
                if po.command not in command_map:
                    command_map[po.command] = {
                        "command": po.command,
                        "pre_output": None,
                        "post_output": po.output,
                        "has_postcheck": True
                    }
                else:
                    command_map[po.command]["post_output"] = po.output
                    command_map[po.command]["has_postcheck"] = True
            
            # Convert map to list sorted by command
            commands_output = list(command_map.values())
            commands_output.sort(key=lambda x: x["command"])
            
            devices_output.append({
                "device_ip": precheck.device_ip,
                "precheck_id": str(precheck.id),
                "postcheck_id": str(postcheck.id) if postcheck else None,
                "precheck_status": precheck.status,
                "postcheck_status": postcheck.status if postcheck else None,
                "commands": commands_output
            })
        
        return {
            "batch_id": batch_id,
            "status": batch.status,
            "total_devices": batch.total_devices,
            "completed_devices": batch.completed_devices,
            "devices": devices_output
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting batch outputs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get batch outputs: {str(e)}"
        ) 