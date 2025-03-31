import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import traceback
import sys

from .config import settings
from .api.v1.endpoints.precheck import router as precheck_router
from .api.v1.endpoints.postcheck import router as postcheck_router
from .api.v1.endpoints.diff import router as diff_router
from .api.v1.endpoints.status import router as status_router
from .api.v1.endpoints.checks import router as checks_router
from .database import init_db
from .core.logging_config import setup_logging
from .core.device_handler import F5DeviceHandler
from .core.device_manager import DeviceManager

# Set up centralized logging
logger = setup_logging(getattr(logging, settings.LOG_LEVEL, logging.INFO))

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API for managing F5 device configuration verification checks"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(time.time())
    
    logger.info(f"[{request_id}] Request started: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] Request completed: {request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.4f}s"
        )
        return response
    except ValueError as ve:
        # Handle validation errors separately
        process_time = time.time() - start_time
        logger.error(
            f"[{request_id}] Validation error: {request.method} {request.url.path} - "
            f"{process_time:.4f}s - {str(ve)}"
        )
        return JSONResponse(
            status_code=400,
            content={"detail": str(ve)},
        )
    except Exception as e:
        process_time = time.time() - start_time
        exception_details = traceback.format_exception(*sys.exc_info())
        logger.error(
            f"[{request_id}] Request failed: {request.method} {request.url.path} - "
            f"{process_time:.4f}s"
        )
        logger.error(f"[{request_id}] Exception: {str(e)}")
        logger.error(f"[{request_id}] Traceback: {''.join(exception_details)}")
        
        return JSONResponse(
            status_code=500, 
            content={"detail": "Internal server error"},
        )

# Include routers
app.include_router(precheck_router, prefix=settings.API_V1_STR)
app.include_router(postcheck_router, prefix=settings.API_V1_STR)
app.include_router(diff_router, prefix=settings.API_V1_STR)
app.include_router(status_router, prefix=settings.API_V1_STR)
app.include_router(checks_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize application dependencies."""
    logger.info("============= Starting application =============")
    logger.info(f"API Version: {settings.VERSION}")
    
    # Get environment safely with fallback to development
    environment = getattr(settings, "ENVIRONMENT", "development")
    logger.info(f"Environment: {environment}")
    
    # Initialize DeviceManager
    DeviceManager()
    logger.info("Device Manager initialized")
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.critical(f"Database initialization failed: {str(e)}")
        logger.exception("Database initialization error details:")
        raise
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources."""
    logger.info("Shutting down application")
    
    # Close all device connections
    logger.info("Closing all device handlers")
    DeviceManager().close_all()
    
    logger.info("Application shutdown complete")

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    logger.info("Root endpoint accessed")
    return {
        "message": "F5 Pre/Post Check API",
        "version": settings.VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    logger.debug("Health check endpoint accessed")
    return {
        "status": "healthy",
        "timestamp": time.time()
    } 