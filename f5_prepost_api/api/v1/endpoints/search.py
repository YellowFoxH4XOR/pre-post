from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging

from ....database import get_db, CheckBatch, PreCheck, PostCheck
from ....models.schemas import BatchSearchResponse

router = APIRouter()

# Get logger
logger = logging.getLogger(__name__)

@router.get("/search/batches", response_model=BatchSearchResponse)
async def search_batches_by_user(
    username: str = Query(..., description="Username to search for"),
    db: AsyncSession = Depends(get_db)
):
    """Search for batch operations by username.
    
    Args:
        username: Username to search for
        db: Database session
        
    Returns:
        200: List of batch operations
        500: Internal server error
    """
    try:
        logger.info(f"Searching for batches by username: {username}")
        
        # Create query to find batches by username
        query = select(CheckBatch).filter(CheckBatch.created_by == username)
        
        # Execute query
        result = await db.execute(query)
        batches = result.scalars().all()
        
        logger.info(f"Found {len(batches)} batches for user: {username}")
        
        # Build response
        batch_list = []
        for batch in batches:
            # Get the count of prechecks for this batch
            precheck_query = select(PreCheck).filter(PreCheck.batch_id == batch.batch_id)
            precheck_result = await db.execute(precheck_query)
            prechecks = precheck_result.scalars().all()
            
            # Get all associated postchecks
            postcheck_count = 0
            for precheck in prechecks:
                postcheck_query = select(PostCheck).filter(PostCheck.precheck_id == precheck.id)
                postcheck_result = await db.execute(postcheck_query)
                postchecks = postcheck_result.scalars().all()
                postcheck_count += len(postchecks)
            
            # Construct batch details
            batch_list.append({
                "batch_id": str(batch.batch_id),
                "created_at": batch.created_at,
                "status": batch.status,
                "total_devices": batch.total_devices,
                "completed_devices": batch.completed_devices,
                "precheck_count": len(prechecks),
                "postcheck_count": postcheck_count
            })
        
        # Return batches in reverse chronological order (newest first)
        batch_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "username": username,
            "total_batches": len(batch_list),
            "batches": batch_list
        }
    except Exception as e:
        logger.exception(f"Error searching batches: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search batches: {str(e)}"
        ) 