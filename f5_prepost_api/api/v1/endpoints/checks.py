from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_, and_
import logging

from ....database import get_db, CheckBatch, PreCheck, PostCheck
from ....models.schemas import CheckListResponse

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

@router.get("/checks", response_model=CheckListResponse)
async def list_checks(
    device_ip: Optional[str] = None,
    status: Optional[str] = None,
    batch_id: Optional[UUID] = None,
    days: Optional[int] = Query(None, ge=1, le=30, description="Limit to checks within the last N days"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    List checks with optional filtering.
    
    Returns:
        200: List of checks
        500: Internal server error
    """
    try:
        logger.info(f"Listing checks with filters: device_ip={device_ip}, status={status}, batch_id={batch_id}, days={days}")
        
        # Base query for prechecks
        precheck_query = (
            select(
                PreCheck.id.label("check_id"),
                PreCheck.batch_id,
                PreCheck.device_ip,
                PreCheck.status,
                PreCheck.created_by,
                PreCheck.timestamp,
                func.literal("precheck").label("type")
            )
        )
        
        # Apply filters to prechecks
        precheck_filters = []
        if device_ip:
            precheck_filters.append(PreCheck.device_ip == device_ip)
        if status:
            precheck_filters.append(PreCheck.status == status)
        if batch_id:
            precheck_filters.append(PreCheck.batch_id == str(batch_id))
        if days:
            date_limit = datetime.utcnow() - timedelta(days=days)
            precheck_filters.append(PreCheck.timestamp >= date_limit)
        
        if precheck_filters:
            precheck_query = precheck_query.where(and_(*precheck_filters))
        
        # Query for postchecks - join with prechecks to get batch_id
        postcheck_query = (
            select(
                PostCheck.id.label("check_id"),
                PreCheck.batch_id,
                PreCheck.device_ip,
                PostCheck.status,
                PostCheck.created_by,
                PostCheck.timestamp,
                func.literal("postcheck").label("type")
            )
            .join(PreCheck, PostCheck.precheck_id == PreCheck.id)
        )
        
        # Apply the same filters to postchecks
        postcheck_filters = []
        if device_ip:
            postcheck_filters.append(PreCheck.device_ip == device_ip)
        if status:
            postcheck_filters.append(PostCheck.status == status)
        if batch_id:
            postcheck_filters.append(PreCheck.batch_id == str(batch_id))
        if days:
            date_limit = datetime.utcnow() - timedelta(days=days)
            postcheck_filters.append(PostCheck.timestamp >= date_limit)
        
        if postcheck_filters:
            postcheck_query = postcheck_query.where(and_(*postcheck_filters))
        
        # Combine queries with union
        union_query = precheck_query.union(postcheck_query)
        
        # Apply order and pagination
        final_query = union_query.order_by("timestamp").offset((page - 1) * page_size).limit(page_size)
        
        # Count query
        count_query = select(func.count()).select_from(union_query.subquery())
        
        # Execute queries
        result = await db.execute(final_query)
        count_result = await db.execute(count_query)
        
        # Process results
        checks = result.all()
        total = count_result.scalar_one() or 0
        
        logger.info(f"Found {total} checks, returning page {page} with {len(checks)} items")
        
        # Format the response - carefully handling attributes to avoid KeyErrors
        return {
            "checks": [
                {
                    "check_id": str(check.check_id),
                    "batch_id": str(check.batch_id),
                    "device_ip": check.device_ip,
                    "type": check.type,
                    "status": check.status,
                    "timestamp": check.timestamp
                }
                for check in checks
            ],
            "total": total,
            "page": page
        }
    except Exception as e:
        logger.exception(f"Error listing checks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list checks: {str(e)}"
        ) 