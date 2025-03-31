from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from datetime import datetime

from ....database import get_db, CheckBatch, PreCheck, PreCheckOutput
from ....models.schemas import (
    PreCheckRequest,
    PreCheckResponse,
    DeviceCredentials
)
from ....core.device_handler import F5DeviceHandler

router = APIRouter()

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
        batch_id = str(uuid.uuid4())
        checks = []
        
        # Create batch record
        batch = CheckBatch(
            batch_id=batch_id,
            status="in_progress",
            total_devices=len(request.devices),
            completed_devices=0,
            created_by=request.created_by if hasattr(request, 'created_by') else None
        )
        db.add(batch)
        
        for device in request.devices:
            handler = F5DeviceHandler(
                device_ip=device.device_ip,
                username=device.username,
                password=device.password
            )
            
            result = await handler.execute_commands_async(request.commands)
            precheck_id = str(uuid.uuid4())
            
            # Create precheck record
            precheck = PreCheck(
                id=precheck_id,
                device_ip=device.device_ip,
                status="completed" if result["status"] == "success" else "failed",
                created_by=request.created_by if hasattr(request, 'created_by') else None,
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
                checks.append({
                    "device_ip": device.device_ip,
                    "precheck_id": precheck_id,
                    "status": "failed"
                })
        
        batch.status = "completed" if batch.completed_devices == batch.total_devices else "partial"
        await db.commit()
        
        return {
            "batch_id": batch_id,
            "checks": checks,
            "timestamp": datetime.utcnow(),
            "message": "PreCheck initiated successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create precheck: {str(e)}"
        ) 