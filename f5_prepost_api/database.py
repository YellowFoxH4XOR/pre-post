from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.sqlite import BLOB
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database engine and session setup
engine = create_async_engine(
    "sqlite+aiosqlite:///f5_prepost.db",
    echo=True,
    connect_args={"check_same_thread": False}
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Database dependency
async def get_db():
    """Get database session with transaction management."""
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        await session.close()

# Initialize database
async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")

# Models
class CheckBatch(Base):
    """Represents a batch of pre/post checks with status tracking."""
    __tablename__ = "check_batches"
    
    batch_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # "initiated", "in_progress", "partial", "completed", "failed"
    total_devices = Column(Integer)
    completed_devices = Column(Integer, default=0)
    created_by = Column(String)

    # Relationships
    prechecks = relationship("PreCheck", back_populates="batch", cascade="all, delete-orphan")

class PreCheck(Base):
    """Stores pre-change verification data for F5 devices."""
    __tablename__ = "prechecks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("check_batches.batch_id"))
    device_ip = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # "in_progress", "completed", "failed"
    created_by = Column(String)
    meta_data = Column(JSON)  # Store commands and other metadata
    
    # Relationships
    batch = relationship("CheckBatch", back_populates="prechecks")
    outputs = relationship("PreCheckOutput", back_populates="precheck", cascade="all, delete-orphan")
    postchecks = relationship("PostCheck", back_populates="precheck", cascade="all, delete-orphan")

class PreCheckOutput(Base):
    """Stores command outputs from pre-change verification."""
    __tablename__ = "precheck_outputs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    precheck_id = Column(String(36), ForeignKey("prechecks.id"))
    command = Column(String)
    output = Column(String)
    execution_order = Column(Integer)
    
    # Relationships
    precheck = relationship("PreCheck", back_populates="outputs")

class PostCheck(Base):
    """Stores post-change verification data for F5 devices."""
    __tablename__ = "postchecks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    precheck_id = Column(String(36), ForeignKey("prechecks.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # "in_progress", "completed", "failed"
    created_by = Column(String)
    
    # Relationships
    precheck = relationship("PreCheck", back_populates="postchecks")
    outputs = relationship("PostCheckOutput", back_populates="postcheck", cascade="all, delete-orphan")

class PostCheckOutput(Base):
    """Stores command outputs from post-change verification."""
    __tablename__ = "postcheck_outputs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    postcheck_id = Column(String(36), ForeignKey("postchecks.id"))
    command = Column(String)
    output = Column(String)
    execution_order = Column(Integer)
    
    # Relationships
    postcheck = relationship("PostCheck", back_populates="outputs")

class Diff(Base):
    """Stores generated diffs between pre and post outputs."""
    __tablename__ = "diffs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    precheck_id = Column(String(36), ForeignKey("prechecks.id"))
    postcheck_id = Column(String(36), ForeignKey("postchecks.id"))
    command = Column(String)
    diff_output = Column(String)
    changes_detected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow) 