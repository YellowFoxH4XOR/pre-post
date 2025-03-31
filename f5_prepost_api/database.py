from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.sqlite import BLOB  # Changed from PostgreSQL UUID
import uuid
from datetime import datetime

# Change the database URL from in-memory to file-based
engine = create_async_engine(
    "sqlite+aiosqlite:///f5_prepost.db",  # Changed from :memory: to file path
    echo=True,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

class CheckBatch(Base):
    """Represents a batch of pre/post checks with status tracking."""
    __tablename__ = "check_batches"
    
    # Changed UUID to String for SQLite compatibility
    batch_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    total_devices = Column(Integer)
    completed_devices = Column(Integer, default=0)
    created_by = Column(String)

class PreCheck(Base):
    """Stores pre-change verification data for F5 devices."""
    __tablename__ = "prechecks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_ip = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    created_by = Column(String)
    meta_data = Column(JSON)
    outputs = relationship("PreCheckOutput", back_populates="precheck")
    postcheck = relationship("PostCheck", back_populates="precheck")

class PreCheckOutput(Base):
    """Stores command outputs from pre-change checks."""
    __tablename__ = "precheck_outputs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    precheck_id = Column(String(36), ForeignKey("prechecks.id"))
    command = Column(String)
    output = Column(String)
    execution_order = Column(Integer)
    precheck = relationship("PreCheck", back_populates="outputs")

class PostCheck(Base):
    """Stores post-change verification data for F5 devices."""
    __tablename__ = "postchecks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    precheck_id = Column(String(36), ForeignKey("prechecks.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    created_by = Column(String)
    outputs = relationship("PostCheckOutput", back_populates="postcheck")
    precheck = relationship("PreCheck", back_populates="postcheck")

class PostCheckOutput(Base):
    """Stores command outputs from post-change checks."""
    __tablename__ = "postcheck_outputs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    postcheck_id = Column(String(36), ForeignKey("postchecks.id"))
    command = Column(String)
    output = Column(String)
    execution_order = Column(Integer)
    postcheck = relationship("PostCheck", back_populates="outputs")

# Database initialization function
async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Database dependency
async def get_db():
    """Dependency for database session management."""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close() 