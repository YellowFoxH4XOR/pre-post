from typing import Dict, Any
import difflib
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select
import logging

from ..database import PreCheckOutput, PostCheckOutput

# Configure logging
logger = logging.getLogger(__name__)

async def generate_diff(
    precheck_id: UUID,
    postcheck_id: UUID,
    device_ip: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Generate diff between pre and post-check command outputs."""
    logger.info(f"Generating diff for device: {device_ip}, precheck: {precheck_id}, postcheck: {postcheck_id}")
    
    # Always convert UUID to string for SQLite compatibility
    pre_id_str = str(precheck_id)
    post_id_str = str(postcheck_id)
    
    pre_stmt = select(PreCheckOutput).filter(
        PreCheckOutput.precheck_id == pre_id_str
    )
    post_stmt = select(PostCheckOutput).filter(
        PostCheckOutput.postcheck_id == post_id_str
    )
    
    pre_result = await db.execute(pre_stmt)
    post_result = await db.execute(post_stmt)
    
    pre_outputs = pre_result.scalars().all()
    post_outputs = post_result.scalars().all()
    
    logger.info(f"Found {len(pre_outputs)} pre-outputs and {len(post_outputs)} post-outputs for device: {device_ip}")
    
    total_commands = len(pre_outputs)
    changes_detected = 0
    
    diff_results = {}
    
    for pre, post in zip(pre_outputs, post_outputs):
        if pre.command != post.command:
            logger.warning(f"Command mismatch: {pre.command} vs {post.command} for device: {device_ip}")
            continue
        
        logger.info(f"Comparing command output for device: {device_ip}, command: {pre.command}")
        
        diff = list(difflib.unified_diff(
            pre.output.splitlines(),
            post.output.splitlines(),
            fromfile=f'pre_{pre.command}',
            tofile=f'post_{pre.command}',
            lineterm=''
        ))
        
        if diff:
            changes_detected += 1
            diff_results[pre.command] = diff
            logger.info(f"Changes detected for device: {device_ip}, command: {pre.command}, diff lines: {len(diff)}")
        else:
            logger.info(f"No changes detected for device: {device_ip}, command: {pre.command}")
    
    logger.info(f"Diff generation completed for device: {device_ip}, total commands: {total_commands}, commands with changes: {changes_detected}")
    
    return {
        "status": "completed",
        "total_commands": total_commands,
        "changes": changes_detected,
        "diffs": diff_results
    } 