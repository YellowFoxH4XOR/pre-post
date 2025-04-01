from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from typing import List, Optional
import logging
from datetime import datetime

from ....database import get_db, CheckBatch, PreCheck, PostCheck
from ....models.schemas import CheckListResponse, CheckListItem

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

@router.get("/checks", response_model=CheckListResponse)
async def list_checks(
    device_ip: Optional[str] = None,
    status: Optional[str] = None,
    check_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List and filter check operations.
    
    Args:
        device_ip: Filter by device IP
        status: Filter by status
        check_type: Filter by check type (precheck or postcheck)
        start_date: Filter by date range start
        end_date: Filter by date range end
        page: Pagination page number
        limit: Number of items per page
        db: Database session
        
    Returns:
        200: List of checks
        500: Internal server error
    """
    try:
        logger.info(f"Listing checks with filters: device_ip={device_ip}, status={status}, check_type={check_type}")
        
        # Build the combined response of prechecks and postchecks
        result = []
        offset = (page - 1) * limit
        
        # Get prechecks with filters
        pre_query = select(PreCheck)
        
        # Apply filters for prechecks
        filters = []
        if device_ip:
            filters.append(PreCheck.device_ip == device_ip)
        if status:
            filters.append(PreCheck.status == status)
        if start_date:
            filters.append(PreCheck.timestamp >= start_date)
        if end_date:
            filters.append(PreCheck.timestamp <= end_date)
            
        if filters:
            pre_query = pre_query.filter(and_(*filters))
            
        pre_query = pre_query.order_by(PreCheck.timestamp.desc())
        pre_query = pre_query.offset(offset).limit(limit)
        
        pre_result = await db.execute(pre_query)
        prechecks = pre_result.scalars().all()
        
        # Get postchecks with same filters
        post_query = select(PostCheck)
        
        # Apply filters for postchecks
        filters = []
        if device_ip:
            # Need to join with PreCheck to filter by device_ip
            post_query = post_query.join(PreCheck, PostCheck.precheck_id == PreCheck.id)
            filters.append(PreCheck.device_ip == device_ip)
        if status:
            filters.append(PostCheck.status == status)
        if start_date:
            filters.append(PostCheck.timestamp >= start_date)
        if end_date:
            filters.append(PostCheck.timestamp <= end_date)
            
        if filters:
            post_query = post_query.filter(and_(*filters))
            
        post_query = post_query.order_by(PostCheck.timestamp.desc())
        post_query = post_query.offset(offset).limit(limit)
        
        post_result = await db.execute(post_query)
        postchecks = post_result.scalars().all()
        
        # Build the response
        for precheck in prechecks:
            if not check_type or check_type.lower() == "precheck":
                result.append({
                    "check_id": str(precheck.id),
                    "batch_id": str(precheck.batch_id),
                    "type": "precheck",
                    "device_ip": precheck.device_ip,
                    "status": precheck.status,
                    "timestamp": precheck.timestamp
                })
        
        for postcheck in postchecks:
            if not check_type or check_type.lower() == "postcheck":
                # Get the associated precheck to get device_ip and batch_id
                precheck_query = select(PreCheck).filter(PreCheck.id == postcheck.precheck_id)
                precheck_result = await db.execute(precheck_query)
                related_precheck = precheck_result.scalars().first()
                
                if related_precheck:
                    result.append({
                        "check_id": str(postcheck.id),
                        "batch_id": str(related_precheck.batch_id),
                        "type": "postcheck",
                        "device_ip": related_precheck.device_ip,
                        "status": postcheck.status,
                        "timestamp": postcheck.timestamp
                    })
        
        # Sort results by timestamp (newest first)
        result.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination to the combined sorted result
        paginated_result = result[:limit]
        
        return {
            "checks": paginated_result,
            "total": len(result),
            "page": page
        }
    except Exception as e:
        logger.exception(f"Error listing checks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list checks: {str(e)}"
        ) 