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
from ....database import get_async_session
from ....utils.command_validator import validate_read_only_commands

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
        400: Invalid request data or precheck failed
        500: Internal server error
    """
    try:
        logger.info(f"Creating postcheck for batch: {batch_id}")
        
        # First check the batch exists - using a separate session
        async with get_async_session() as batch_session:
            batch_stmt = select(CheckBatch).filter(CheckBatch.batch_id == str(batch_id))
            batch_result = await batch_session.execute(batch_stmt)
            batch = batch_result.scalar_one_or_none()
            
            if not batch:
                logger.warning(f"Batch not found: {batch_id}")
                raise HTTPException(status_code=404, detail="Batch not found")
            
            # Store relevant batch data
            batch_data = {
                "id": batch.batch_id,
                "status": batch.status,
                "completed_devices": batch.completed_devices
            }
            
        # Get the associated prechecks with another separate session
        async with get_async_session() as precheck_session:
            pre_stmt = select(PreCheck).filter(PreCheck.batch_id == str(batch_id))
            pre_result = await precheck_session.execute(pre_stmt)
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
        
        # Process device checks and save results in main transaction
        checks = []
        completed_devices = 0
        total_processed = 0
        
        # Main transaction for saving postchecks
        async with get_async_session() as postcheck_session:
            async with postcheck_session.begin():
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
                    postcheck_session.add(postcheck)
                    
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
                            postcheck_session.add(postcheck_output)
                        
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
                
                # Final batch update in separate transaction
                async with get_async_session() as batch_update_session:
                    async with batch_update_session.begin():
                        batch_update_stmt = select(CheckBatch).filter(CheckBatch.batch_id == str(batch_id))
                        batch_result = await batch_update_session.execute(batch_update_stmt)
                        batch_to_update = batch_result.scalar_one_or_none()
                        
                        if batch_to_update:
                            if completed_devices == total_processed:
                                batch_to_update.status = "completed"
                            elif completed_devices > 0:
                                batch_to_update.status = "partial"
                            else:
                                batch_to_update.status = "failed"
                                
                            batch_to_update.completed_devices = completed_devices
        
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