# F5 Pre/Post Check API Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Components](#system-components)
3. [API Endpoints](#api-endpoints)
4. [Database Schema](#database-schema)
5. [Status Definitions](#status-definitions)
6. [Project Structure](#project-structure)
7. [Connection Management](#connection-management)
8. [Key Considerations](#key-considerations)
9. [Process Flow](#process-flow)

## Overview
This API system is designed to perform pre and post-change verification checks on F5 load balancer devices. It executes specified commands before and after changes, stores the results, and provides diff comparisons with support for multiple devices.

## System Components

### Core Entities

#### 1. PreCheck
- Unique identifier
- Device information
- Timestamp
- Command outputs
- Status
- User information

#### 2. PostCheck
- ID (linked to precheck)
- Timestamp
- Command outputs
- Status
- User information

#### 3. DiffResult
- PreCheck ID
- PostCheck ID
- Diff output
- Status

#### 4. DeviceManager
- Connection pooling
- Session reuse
- Lifecycle management

## API Endpoints

### 1. PreCheck API
```http
POST /api/v1/precheck
```
#### Request Body
```json
{
  "devices": [
    {
      "device_ip": "string",
      "username": "string",
      "password": "string"
    }
  ],
  "commands": ["string"]
}
```
#### Response
```json
{
  "batch_id": "string",
  "checks": [
    {
      "device_ip": "string",
      "precheck_id": "string",
      "status": "string"
    }
  ],
  "timestamp": "datetime",
  "message": "string"
}
```

### 2. PostCheck API
```http
POST /api/v1/postcheck/{batch_id}
```
#### Request Body
```json
{
  "devices": [
    {
      "device_ip": "string",
      "username": "string",
      "password": "string"
    }
  ]
}
```
#### Response
```json
{
  "batch_id": "string",
  "checks": [
    {
      "device_ip": "string",
      "postcheck_id": "string",
      "precheck_id": "string",
      "status": "string"
    }
  ],
  "timestamp": "datetime",
  "message": "string"
}
```

### 3. Diff API
```http
GET /api/v1/batch/{batch_id}/diff
```
#### Response
```json
{
  "batch_id": "string",
  "devices": [
    {
      "device_ip": "string",
      "precheck_id": "string",
      "postcheck_id": "string",
      "status": "string",
      "summary": {
        "total_commands": "integer",
        "commands_with_changes": "integer",
        "timestamp": "datetime"
      }
    }
  ],
  "overall_status": "string"
}
```

### 4. Status Check API
```http
GET /api/v1/batch/{batch_id}/status
```
#### Response
```json
{
  "batch_id": "string",
  "total_devices": "integer",
  "completed_devices": "integer",
  "status": "string",
  "devices": [
    {
      "device_ip": "string",
      "precheck_id": "string",
      "postcheck_id": "string",
      "status": "string",
      "progress": "integer"
    }
  ]
}
```

### 5. List Checks API
```http
GET /api/v1/checks
```
#### Query Parameters
- device_ip (optional)
- status (optional)
- date_range (optional)
- batch_id (optional)

#### Response
```json
{
  "checks": [
    {
      "check_id": "string",
      "batch_id": "string",
      "type": "string",
      "device_ip": "string",
      "status": "string",
      "timestamp": "datetime"
    }
  ],
  "total": "integer",
  "page": "integer"
}
```

## Database Schema

### Tables

#### check_batches
```sql
- batch_id: UUID (primary key)
- created_at: datetime
- status: enum
- total_devices: integer
- completed_devices: integer
- created_by: string
```

#### batch_checks
```sql
- id: UUID (primary key)
- batch_id: UUID (foreign key)
- check_id: UUID (foreign key)
- device_ip: string
- check_type: enum (precheck/postcheck)
- status: enum
- created_at: datetime
```

#### prechecks
```sql
- id: UUID (primary key)
- device_ip: string
- timestamp: datetime
- status: enum
- created_by: string
- metadata: jsonb
```

#### precheck_outputs
```sql
- id: UUID (primary key)
- precheck_id: UUID (foreign key)
- command: string
- output: text
- execution_order: int
```

#### postchecks
```sql
- id: UUID (primary key)
- precheck_id: UUID (foreign key)
- timestamp: datetime
- status: enum
- created_by: string
```

#### postcheck_outputs
```sql
- id: UUID (primary key)
- postcheck_id: UUID (foreign key)
- command: string
- output: text
- execution_order: int
```

#### diffs
```sql
- id: UUID (primary key)
- precheck_id: UUID (foreign key)
- postcheck_id: UUID (foreign key)
- command: string
- diff_output: text
- changes_detected: boolean
```

#### devices
```sql
- device_ip: string (primary key)
- hostname: string
- last_check_status: enum
- last_checked: datetime
- created_at: datetime
- updated_at: datetime
```

## Status Definitions

### Check Status
- INITIATED
- IN_PROGRESS
- COMPLETED
- FAILED

### Batch Status
- INITIATED
- IN_PROGRESS
- PARTIALLY_COMPLETED
- COMPLETED
- FAILED

### Diff Status
- PENDING
- PROCESSING
- COMPLETED
- FAILED

## Connection Management

The system implements optimized connection management for F5 devices:

### DeviceHandler
- Uses Netmiko for device communication
- Maintains persistent connections
- Reuses sessions for multiple commands
- Detects and handles stale connections
- Provides graceful error handling

### DeviceManager
- Singleton pattern for application-wide management
- Caches device handler instances
- Provides connection pooling across API requests
- Ensures proper resource cleanup

### Connection Lifecycle
1. **Creation**: On first device access
2. **Reuse**: Subsequent commands use existing connection
3. **Verification**: Connection liveness checked before reuse
4. **Recovery**: Automatic reconnection if connection lost
5. **Cleanup**: Proper disconnection on application shutdown

### Benefits
- Reduced authentication overhead
- Lower connection latency
- Improved command execution performance
- Better resource utilization
- Enhanced reliability for multi-command operations

## Key Considerations

### Security
- Secure credential handling
- Encryption in transit
- Access control
- Audit logging
- Proper connection cleanup

### Error Handling
- Network timeouts
- Invalid commands
- Device access issues
- Connection failures and recovery
- Data validation
- Individual device failures
- Batch partial completion

### Monitoring
- Command execution times
- Success/failure rates
- Resource usage
- API metrics
- Connection pool statistics
- Batch progress tracking
- Individual device progress tracking
- Overall batch statistics

## Process Flow

### Batch PreCheck Process
1. Receive request with multiple devices
2. Create batch record
3. For each device:
   - Create/reuse device connection
   - Create individual precheck
   - Execute commands in parallel
   - Update batch progress
4. Return batch_id and individual check statuses

### Batch PostCheck Process
1. Receive request with batch_id
2. Validate batch exists
3. For each device in batch:
   - Create/reuse device connection
   - Create individual postcheck
   - Execute commands in parallel
   - Update batch progress
4. Return batch results

### Diff Process
1. Run in background after postcheck
2. Compare outputs
3. Store diff results
4. Make available via API