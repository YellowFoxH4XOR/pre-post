from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select
import logging

from ....database import get_db, PreCheck, PostCheck, PostCheckOutput, CheckBatch
from ....models.schemas import PostCheckRequest, PostCheckResponse
from ....core.device_handler import F5DeviceHandler
from ....core.device_manager import DeviceManager

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

# Get device manager instance
device_manager = DeviceManager()

@router.post("/postcheck/{batch_id}", response_model=PostCheckResponse, status_code=201)
async def create_postcheck(
    batch_id: UUID,
    request: PostCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create post-change verification check for F5 devices.
    
    Returns:
        201: PostCheck successfully created
        404: Batch not found
        400: Invalid request data or commands
        500: Internal server error
    """
    try:
        # Validate commands before processing devices
        invalid_commands = []
        for command in request.commands:
            if not (command.lower().startswith('show ') or 
                   command.lower() == 'show' or
                   command.lower().startswith('list ') or
                   command.lower() == 'list' or
                   command.lower().startswith('display ') or
                   command.lower().startswith('tmsh ') or
                   command.lower() == 'tmsh' or
                   command.lower().startswith('cat ') or
                   command.lower() == 'cat'):
                invalid_commands.append(command)
        
        if invalid_commands:
            error_msg = f"Only show, tmsh, cat, list, and display commands are allowed. Invalid commands: {', '.join(invalid_commands)}"
            logger.error(f"Command validation failed at endpoint level: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
            
        logger.info(f"Creating postcheck for batch: {batch_id}")
        
        # First check the batch exists - outside the transaction
        batch_stmt = select(CheckBatch).filter(CheckBatch.batch_id == str(batch_id))
        batch_result = await db.execute(batch_stmt)
        batch = batch_result.scalar_one_or_none()
        
        if not batch:
            logger.warning(f"Batch not found: {batch_id}")
            raise HTTPException(status_code=404, detail="Batch not found")
            
        # Use a transaction for all database operations
        async with db.begin():
            # Get the associated prechecks
            pre_stmt = select(PreCheck).filter(PreCheck.batch_id == str(batch_id))
            pre_result = await db.execute(pre_stmt)
            prechecks = pre_result.scalars().all()
            
            if not prechecks:
                logger.warning(f"PreChecks not found for batch: {batch_id}")
                raise HTTPException(status_code=404, detail="PreChecks not found for this batch")
            
            # Verify that all prechecks were successful
            failed_prechecks = [p for p in prechecks if p.status == "failed"]
            if failed_prechecks:
                logger.warning(f"Cannot run postcheck: {len(failed_prechecks)} prechecks failed")
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot run postcheck: {len(failed_prechecks)} prechecks failed. Fix issues and run precheck again."
                )
            
            # Map device IPs to their precheck records for easy lookup
            precheck_map = {p.device_ip: p for p in prechecks}
            
            checks = []
            completed_devices = 0
            total_processed = 0
            
            for device in request.devices:
                # Get the corresponding precheck for this device
                precheck = precheck_map.get(device.device_ip)
                if not precheck:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No precheck found for device {device.device_ip}"
                    )
                
                # Get handler from device manager - reuse if possible
                handler = device_manager.get_handler(
                    device_ip=device.device_ip,
                    username=device.username,
                    password=device.password
                )
                
                commands = precheck.meta_data.get("commands", [])
                if not commands:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No commands found in precheck for device {device.device_ip}"
                    )
                
                result = await handler.execute_commands_async(commands)
                postcheck_id = str(uuid4())
                
                # Create postcheck record
                postcheck = PostCheck(
                    id=postcheck_id,
                    precheck_id=precheck.id,
                    status="completed" if result["status"] == "success" else "failed",
                    created_by=request.created_by if hasattr(request, 'created_by') else None
                )
                db.add(postcheck)
                
                total_processed += 1
                
                if result["status"] == "success":
                    # Save command outputs
                    for idx, (command, output) in enumerate(result["results"].items()):
                        postcheck_output = PostCheckOutput(
                            postcheck_id=postcheck_id,
                            command=command,
                            output=output,
                            execution_order=idx
                        )
                        db.add(postcheck_output)
                    
                    completed_devices += 1
                    checks.append({
                        "device_ip": device.device_ip,
                        "precheck_id": precheck.id,
                        "postcheck_id": postcheck_id,
                        "status": "completed"
                    })
                else:
                    checks.append({
                        "device_ip": device.device_ip,
                        "precheck_id": precheck.id,
                        "postcheck_id": postcheck_id,
                        "status": "failed"
                    })
            
            # Update batch status
            if completed_devices == total_processed:
                batch.status = "completed"
            elif completed_devices > 0:
                batch.status = "partial"
            else:
                batch.status = "failed"
                
            batch.completed_devices = completed_devices
            
            # Transaction automatically commits
            
        return {
            "batch_id": batch_id,
            "checks": checks,
            "timestamp": datetime.utcnow(),
            "message": "PostCheck initiated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log full traceback but return simplified message
        logger.exception(f"Error in create_postcheck: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create postcheck: {str(e)}"
        ) 