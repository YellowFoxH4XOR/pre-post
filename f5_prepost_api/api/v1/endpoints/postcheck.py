from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import uuid
from datetime import datetime
import logging

from ....database import get_db, CheckBatch, PreCheck, PostCheck, PostCheckOutput, ensure_str_uuid
from ....models.schemas import (
    PostCheckRequest,
    PostCheckResponse,
    DeviceCredentials
)
from ....core.device_manager import DeviceManager

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

# Get device manager instance
device_manager = DeviceManager()

async def process_postcheck(
    request: PostCheckRequest,
    batch_id: str,
    db_url: str
):
    """Process postcheck operations in the background."""
    from ....database import AsyncSessionLocal
    
    try:
        logger.info(f"Processing postcheck for batch_id: {batch_id}")
        
        # Get batch record in its own session
        async with AsyncSessionLocal() as db_batch:
            stmt = select(CheckBatch).filter(CheckBatch.batch_id == batch_id)
            batch_result = await db_batch.execute(stmt)
            batch = batch_result.scalars().first()
            if not batch:
                logger.error(f"Batch {batch_id} not found")
                return
        
        # Get all prechecks for this batch in another session
        async with AsyncSessionLocal() as db_prechecks:
            stmt = select(PreCheck).filter(PreCheck.batch_id == batch_id)
            precheck_result = await db_prechecks.execute(stmt)
            prechecks = precheck_result.scalars().all()
            
            if not prechecks:
                logger.error(f"No prechecks found for batch_id: {batch_id}")
                return
            
            # Create a mapping of device_ip to precheck
            device_to_precheck = {pc.device_ip: pc for pc in prechecks}
        
        # Process each device with a new session
        for device in request.devices:
            try:
                logger.info(f"Processing postcheck for device: {device.device_ip}")
                
                # Check if there's a precheck for this device
                precheck = device_to_precheck.get(device.device_ip)
                if not precheck:
                    logger.warning(f"No precheck found for device: {device.device_ip}")
                    continue
                
                # Get the commands from precheck metadata
                if not precheck.meta_data or "commands" not in precheck.meta_data:
                    logger.warning(f"No commands found in precheck for device: {device.device_ip}")
                    continue
                
                commands = precheck.meta_data["commands"]
                
                # Get handler
                handler = device_manager.get_handler(
                    device_ip=device.device_ip,
                    username=device.username,
                    password=device.password
                )
                
                # Execute commands
                device_result = await handler.execute_commands_async(commands)
                postcheck_id = str(uuid.uuid4())
                
                # Use a new session for this device's transaction
                async with AsyncSessionLocal() as db_device:
                    async with db_device.begin():
                        # Create postcheck record
                        postcheck = PostCheck(
                            id=postcheck_id,
                            precheck_id=precheck.id,  # Already a string from the database
                            status="completed" if device_result["status"] == "success" else "failed",
                            created_by=request.created_by
                        )
                        db_device.add(postcheck)
                        
                        if device_result["status"] == "success":
                            # Save command outputs
                            for idx, (command, output) in enumerate(device_result["results"].items()):
                                postcheck_output = PostCheckOutput(
                                    postcheck_id=postcheck_id,
                                    command=command,
                                    output=output,
                                    execution_order=idx
                                )
                                db_device.add(postcheck_output)
            except Exception as device_error:
                logger.exception(
                    f"Error processing device {device.device_ip}: {str(device_error)}"
                )
    except Exception as e:
        logger.exception(f"Error processing postcheck: {str(e)}")

@router.post("/postcheck/{batch_id}", response_model=PostCheckResponse, status_code=202)
async def create_postcheck(
    batch_id: str,
    request: PostCheckRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create post-change verification check for F5 devices.
    
    Returns:
        202: PostCheck successfully initiated
        400: Invalid request data
        404: Batch not found
        500: Internal server error
    """
    try:
        logger.info(f"Initiating postcheck for batch_id: {batch_id}")
        
        # Verify batch exists
        stmt = select(CheckBatch).filter(CheckBatch.batch_id == batch_id)
        batch_result = await db.execute(stmt)
        batch = batch_result.scalars().first()
        
        if not batch:
            logger.error(f"Batch not found: {batch_id}")
            raise HTTPException(status_code=404, detail=f"Batch not found: {batch_id}")
        
        # Get all prechecks for this batch
        stmt = select(PreCheck).filter(PreCheck.batch_id == batch_id)
        precheck_result = await db.execute(stmt)
        prechecks = precheck_result.scalars().all()
        
        device_to_precheck = {pc.device_ip: pc for pc in prechecks}
        
        # Prepare response
        checks = []
        for device in request.devices:
            precheck = device_to_precheck.get(device.device_ip)
            checks.append({
                "device_ip": device.device_ip,
                "precheck_id": precheck.id if precheck else None,  # Already a string from database
                "postcheck_id": None,
                "status": "initiated" if precheck else "skipped"
            })
        
        # Schedule background task
        from ....config import settings
        from ....database import DATABASE_URL
        background_tasks.add_task(
            process_postcheck,
            request=request,
            batch_id=batch_id,
            db_url=getattr(settings, 'DATABASE_URL', DATABASE_URL)
        )
        
        return {
            "batch_id": batch_id,
            "checks": checks,
            "timestamp": datetime.utcnow(),
            "message": "PostCheck initiated successfully (processing in background)"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error initiating postcheck: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate postcheck: {str(e)}"
        ) 