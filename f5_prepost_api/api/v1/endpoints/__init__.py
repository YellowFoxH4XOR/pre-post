"""API endpoints for F5 Pre/Post Check operations."""

from .precheck import router as precheck_router
from .postcheck import router as postcheck_router
from .diff import router as diff_router
from .status import router as status_router

__all__ = [
    "precheck_router",
    "postcheck_router",
    "diff_router",
    "status_router"
] 