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
    precheck_id: UUID
    status: str

class PreCheckResponse(BaseModel):
    batch_id: UUID
    checks: List[CheckStatus]
    timestamp: datetime
    message: str

class PostCheckRequest(BaseModel):
    created_by: str
    devices: List[DeviceCredentials]

class PostCheckStatus(BaseModel):
    device_ip: str
    precheck_id: UUID
    postcheck_id: UUID
    status: str

class PostCheckResponse(BaseModel):
    batch_id: UUID
    checks: List[PostCheckStatus]
    timestamp: datetime
    message: str

class DiffSummary(BaseModel):
    total_commands: int
    commands_with_changes: int
    timestamp: datetime

class DiffDeviceStatus(BaseModel):
    device_ip: str
    precheck_id: UUID
    postcheck_id: UUID
    status: str
    summary: DiffSummary

class DiffResponse(BaseModel):
    batch_id: UUID
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