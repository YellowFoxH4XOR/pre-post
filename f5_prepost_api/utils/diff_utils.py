from typing import Dict, Any
import difflib
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select

from ..database import PreCheckOutput, PostCheckOutput

async def generate_diff(
    precheck_id: UUID,
    postcheck_id: UUID,
    device_ip: str,
    db: AsyncSession
) -> Dict[str, Any]:
    """Generate diff between pre and post-check command outputs."""
    pre_stmt = select(PreCheckOutput).filter(
        PreCheckOutput.precheck_id == str(precheck_id)
    )
    post_stmt = select(PostCheckOutput).filter(
        PostCheckOutput.postcheck_id == str(postcheck_id)
    )
    
    pre_result = await db.execute(pre_stmt)
    post_result = await db.execute(post_stmt)
    
    pre_outputs = pre_result.scalars().all()
    post_outputs = post_result.scalars().all()
    
    total_commands = len(pre_outputs)
    changes_detected = 0
    
    diff_results = {}
    
    for pre, post in zip(pre_outputs, post_outputs):
        if pre.command != post.command:
            continue
            
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
    
    return {
        "status": "completed",
        "total_commands": total_commands,
        "changes": changes_detected,
        "diffs": diff_results
    } 