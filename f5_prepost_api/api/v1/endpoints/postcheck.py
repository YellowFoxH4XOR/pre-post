from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import select

from ....database import get_db, PreCheck, PostCheck, PostCheckOutput
from ....models.schemas import PostCheckRequest, PostCheckResponse
from ....core.device_handler import F5DeviceHandler

router = APIRouter()

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
        400: Invalid request data
        500: Internal server error
    """
    try:
        # Update to use select with filter
        print(f"batch_id: {batch_id}")
        stmt = select(PreCheck).filter(PreCheck.id == "cb02b7be-cb5f-4b83-8201-e04d908fca4f")
        print(f"stmt: {stmt}")
        result = await db.execute(stmt)
        print(f"result: {result}")
        precheck = result.scalar_one_or_none()
        print(f"precheck: {precheck}")
        if not precheck:
            raise HTTPException(
                status_code=404,
                detail="Batch not found"
            )
        
        checks = []
        for device in request.devices:
            handler = F5DeviceHandler(
                device_ip=device.device_ip,
                username=device.username,
                password=device.password
            )
            
            result = await handler.execute_commands_async(precheck.meta_data["commands"])
            postcheck_id = str(uuid4())
            
            # Create postcheck record
            postcheck = PostCheck(
                id=postcheck_id,
                precheck_id=str(batch_id),
                status="completed" if result["status"] == "success" else "failed",
                created_by=request.created_by if hasattr(request, 'created_by') else None
            )
            db.add(postcheck)
            
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
                
                checks.append({
                    "device_ip": device.device_ip,
                    "precheck_id": str(batch_id),
                    "postcheck_id": postcheck_id,
                    "status": "completed"
                })
            else:
                checks.append({
                    "device_ip": device.device_ip,
                    "precheck_id": str(batch_id),
                    "postcheck_id": postcheck_id,
                    "status": "failed"
                })
        
        await db.commit()
        
        return {
            "batch_id": batch_id,
            "checks": checks,
            "timestamp": datetime.utcnow(),
            "message": "PostCheck initiated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create postcheck: {str(e)}"
        ) 