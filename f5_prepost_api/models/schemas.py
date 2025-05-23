from pydantic import BaseModel, IPvAnyAddress
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class DeviceCredentials(BaseModel):
    device_ip: str
    username: str
    password: str

class PreCheckRequest(BaseModel):
    created_by: str
    devices: List[DeviceCredentials]
    commands: List[str]

class CheckStatus(BaseModel):
    device_ip: str
    precheck_id: Optional[str] = None
    status: str

class PreCheckResponse(BaseModel):
    batch_id: str
    checks: List[CheckStatus]
    timestamp: datetime
    message: str

class PostCheckRequest(BaseModel):
    created_by: str
    devices: List[DeviceCredentials]

class PostCheckStatus(BaseModel):
    device_ip: str
    precheck_id: Optional[str] = None
    postcheck_id: Optional[str] = None
    status: str

class PostCheckResponse(BaseModel):
    batch_id: str
    checks: List[PostCheckStatus]
    timestamp: datetime
    message: str

class DiffSummary(BaseModel):
    total_commands: int
    commands_with_changes: int
    timestamp: datetime
    diff: Dict

class DiffDeviceStatus(BaseModel):
    device_ip: str
    precheck_id: str
    postcheck_id: Optional[str] = None
    status: str
    summary: Optional[Dict] = None

class DiffResponse(BaseModel):
    batch_id: str
    devices: List[DiffDeviceStatus]
    overall_status: str

class DeviceProgress(BaseModel):
    device_ip: str
    precheck_id: UUID
    postcheck_id: Optional[UUID] = None
    status: str
    status_detail: str
    progress: int

class BatchStatusResponse(BaseModel):
    batch_id: UUID
    total_devices: int
    completed_devices: int
    status: str  # "initiated", "in_progress", "completed", "failed", "partial"
    devices: List[DeviceProgress]

class CheckListItem(BaseModel):
    check_id: UUID
    batch_id: UUID
    type: str
    device_ip: str
    status: str
    timestamp: datetime

class CheckListResponse(BaseModel):
    checks: List[CheckListItem]
    total: int
    page: int

class BatchDetails(BaseModel):
    batch_id: str
    created_at: datetime
    status: str
    total_devices: int
    completed_devices: int
    precheck_count: int
    postcheck_count: int

class BatchSearchResponse(BaseModel):
    username: str
    total_batches: int
    batches: List[BatchDetails]

class CommandOutput(BaseModel):
    command: str
    pre_output: Optional[str] = None
    post_output: Optional[str] = None
    has_postcheck: bool

class DeviceOutput(BaseModel):
    device_ip: str
    precheck_id: str
    postcheck_id: Optional[str] = None
    precheck_status: str
    postcheck_status: Optional[str] = None
    commands: List[CommandOutput]

class BatchOutputResponse(BaseModel):
    batch_id: str
    status: str
    total_devices: int
    completed_devices: int
    devices: List[DeviceOutput] 