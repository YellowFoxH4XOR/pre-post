from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
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

@router.post("/precheck", response_model=PreCheckResponse, status_code=201)
async def create_precheck(
    request: PreCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create pre-change verification check for F5 devices.
    
    Returns:
        201: PreCheck successfully created
        400: Invalid request data
        500: Internal server error
    """
    try:
        logger.info(f"Creating precheck for {len(request.devices)} devices")
        
        # Start transaction
        async with db.begin():
            batch_id = str(uuid.uuid4())
            logger.info(f"Generated batch_id: {batch_id}")
            
            # Create batch record
            batch = CheckBatch(
                batch_id=batch_id,
                status="in_progress",
                total_devices=len(request.devices),
                completed_devices=0,
                created_by=request.created_by if hasattr(request, 'created_by') else None
            )
            db.add(batch)
            
            # Process each device with better error handling
            checks = []
            for device in request.devices:
                try:
                    logger.info(f"Processing device: {device.device_ip}")
                    
                    # Get handler from device manager - reuse if possible
                    handler = device_manager.get_handler(
                        device_ip=device.device_ip,
                        username=device.username,
                        password=device.password
                    )
                    
                    result = await handler.execute_commands_async(request.commands)
                    precheck_id = str(uuid.uuid4())
                    
                    # Create precheck record
                    precheck = PreCheck(
                        id=precheck_id,
                        batch_id=batch_id,
                        device_ip=device.device_ip,
                        status="completed" if result["status"] == "success" else "failed",
                        created_by=(
                            request.created_by 
                            if hasattr(request, 'created_by') 
                            else None
                        ),
                        meta_data={"commands": request.commands}
                    )
                    db.add(precheck)
                    
                    if result["status"] == "success":
                        # Save command outputs
                        for idx, (command, output) in enumerate(result["results"].items()):
                            precheck_output = PreCheckOutput(
                                precheck_id=precheck_id,
                                command=command,
                                output=output,
                                execution_order=idx
                            )
                            db.add(precheck_output)
                        
                        batch.completed_devices += 1
                        checks.append({
                            "device_ip": device.device_ip,
                            "precheck_id": precheck_id,
                            "status": "completed"
                        })
                    else:
                        logger.warning(
                            f"Precheck failed for device: {device.device_ip}, "
                            f"error: {result.get('error', 'Unknown error')}"
                        )
                        checks.append({
                            "device_ip": device.device_ip,
                            "precheck_id": precheck_id,
                            "status": "failed"
                        })
                except Exception as device_error:
                    logger.exception(
                        f"Error processing device {device.device_ip}: {str(device_error)}"
                    )
                    checks.append({
                        "device_ip": device.device_ip,
                        "precheck_id": None,
                        "status": "failed"
                    })
            
            # Update batch status
            batch.status = (
                "completed" 
                if batch.completed_devices == batch.total_devices 
                else "partial"
            )
            logger.info(
                f"Batch status: {batch.status}, "
                f"completed devices: {batch.completed_devices}/{batch.total_devices}"
            )
        
        return {
            "batch_id": batch_id,
            "checks": checks,
            "timestamp": datetime.utcnow(),
            "message": "PreCheck initiated successfully"
        }
    except Exception as e:
        logger.exception(f"Error creating precheck: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create precheck: {str(e)}"
        ) 