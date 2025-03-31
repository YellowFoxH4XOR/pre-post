from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.v1.endpoints import precheck, postcheck, diff, status
from .database import init_db

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

# Include routers
app.include_router(precheck.router, prefix=settings.API_V1_STR)
app.include_router(postcheck.router, prefix=settings.API_V1_STR)
app.include_router(diff.router, prefix=settings.API_V1_STR)
app.include_router(status.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize application dependencies."""
    await init_db()

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "F5 Pre/Post Check API",
        "version": settings.VERSION
    } 