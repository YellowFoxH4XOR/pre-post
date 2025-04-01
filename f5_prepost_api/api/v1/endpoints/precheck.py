from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid
from datetime import datetime
import logging

from ....database import get_db, CheckBatch, PreCheck, PreCheckOutput
from ....models.schemas import (
    PreCheckRequest,
    PreCheckResponse,
    DeviceCredentials
)
from ....core.device_manager import DeviceManager

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

# Get device manager instance
device_manager = DeviceManager()

async def process_precheck(
    request: PreCheckRequest,
    batch_id: str,
    db_url: str
):
    """Process precheck operations in the background."""
    from ....database import AsyncSessionLocal
    
    try:
        logger.info(f"Processing precheck for batch_id: {batch_id}")
        
        # First, get the batch in its own session
        async with AsyncSessionLocal() as db_batch:
            stmt = select(CheckBatch).filter(CheckBatch.batch_id == batch_id)
            batch_query_result = await db_batch.execute(stmt)
            batch = batch_query_result.scalars().first()
            if not batch:
                logger.error(f"Batch {batch_id} not found")
                return
        
        # Process each device with better error handling
        for device in request.devices:
            try:
                logger.info(f"Processing device: {device.device_ip}")
                
                # Get handler from device manager - reuse if possible
                handler = device_manager.get_handler(
                    device_ip=device.device_ip,
                    username=device.username,
                    password=device.password
                )
                
                device_result = await handler.execute_commands_async(request.commands)
                precheck_id = str(uuid.uuid4())
                
                # Use a new session for each device transaction
                async with AsyncSessionLocal() as db_device:
                    async with db_device.begin():
                        # Create precheck record
                        precheck = PreCheck(
                            id=precheck_id,
                            batch_id=batch_id,
                            device_ip=device.device_ip,
                            status="completed" if device_result["status"] == "success" else "failed",
                            created_by=request.created_by if hasattr(request, 'created_by') else None,
                            meta_data={"commands": request.commands}
                        )
                        db_device.add(precheck)
                        
                        if device_result["status"] == "success":
                            # Save command outputs
                            for idx, (command, output) in enumerate(device_result["results"].items()):
                                precheck_output = PreCheckOutput(
                                    precheck_id=precheck_id,
                                    command=command,
                                    output=output,
                                    execution_order=idx
                                )
                                db_device.add(precheck_output)
                
                # Update batch completion count in a separate session
                async with AsyncSessionLocal() as db_update:
                    async with db_update.begin():
                        # Get the latest batch data
                        stmt = select(CheckBatch).filter(CheckBatch.batch_id == batch_id)
                        update_query_result = await db_update.execute(stmt)
                        current_batch = update_query_result.scalars().first()
                        
                        if current_batch and device_result["status"] == "success":
                            current_batch.completed_devices += 1
            except Exception as device_error:
                logger.exception(
                    f"Error processing device {device.device_ip}: {str(device_error)}"
                )
        
        # Update batch status in a final separate session
        async with AsyncSessionLocal() as db_final:
            async with db_final.begin():
                # Get the latest batch data
                stmt = select(CheckBatch).filter(CheckBatch.batch_id == batch_id)
                final_query_result = await db_final.execute(stmt)
                final_batch = final_query_result.scalars().first()
                
                if final_batch:
                    final_batch.status = (
                        "completed" 
                        if final_batch.completed_devices == final_batch.total_devices 
                        else "partial"
                    )
                    logger.info(
                        f"Batch status: {final_batch.status}, "
                        f"completed devices: {final_batch.completed_devices}/{final_batch.total_devices}"
                    )
    except Exception as e:
        logger.exception(f"Error processing precheck: {str(e)}")

@router.post("/precheck", response_model=PreCheckResponse, status_code=202)
async def create_precheck(
    request: PreCheckRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create pre-change verification check for F5 devices.
    
    Returns:
        202: PreCheck successfully initiated
        400: Invalid request data or commands
        500: Internal server error
    """
    try:
        logger.info(f"Initiating precheck for {len(request.devices)} devices")
        
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
        
        # Create batch record in a transaction
        batch_id = str(uuid.uuid4())
        logger.info(f"Generated batch_id: {batch_id}")
        
        async with db.begin():
            batch = CheckBatch(
                batch_id=batch_id,
                status="initiated",
                total_devices=len(request.devices),
                completed_devices=0,
                created_by=request.created_by if hasattr(request, 'created_by') else None
            )
            db.add(batch)
            
        # Prepare response
        checks = []
        for device in request.devices:
            checks.append({
                "device_ip": device.device_ip,
                "precheck_id": None,
                "status": "initiated"
            })
        
        # Schedule background task
        from ....config import settings
        from ....database import DATABASE_URL
        background_tasks.add_task(
            process_precheck,
            request=request,
            batch_id=batch_id,
            db_url=getattr(settings, 'DATABASE_URL', DATABASE_URL)
        )
        
        return {
            "batch_id": batch_id,
            "checks": checks,
            "timestamp": datetime.utcnow(),
            "message": "PreCheck initiated successfully (processing in background)"
        }
    except Exception as e:
        logger.exception(f"Error initiating precheck: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate precheck: {str(e)}"
        ) 