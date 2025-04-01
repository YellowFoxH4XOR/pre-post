# F5 Pre/Post Check API

A FastAPI-based system for managing F5 device configuration verification checks.

## Features

- Pre-change configuration checks
- Post-change verification
- Configuration diff generation
- Batch operations support
- Connection pooling and reuse
- Async database operations
- SQLite storage
- **NEW** Background processing for improved performance
- **NEW** Comprehensive command output and diff visualization
- **NEW** Batch search by username
- **NEW** Precheck/Postcheck outputs view

## Prerequisites

- Python 3.11 or higher
- Poetry (Python package manager)
- F5 device access credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd f5-prepost-api
```

2. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Create environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
DATABASE_URL=sqlite+aiosqlite:///f5_prepost.db
# Add your secure configuration here
```

## Database Setup

The database will be automatically created when you first run the application. The tables will be created based on the SQLAlchemy models.

## Running the Application

1. Activate the poetry environment:
```bash
poetry shell
```

2. Start the API server:
```bash
uvicorn f5_prepost_api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## API Documentation

Once running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## API Endpoints

### 1. Pre-Check API
```http
POST /api/v1/precheck
```
Creates a pre-change verification check for F5 devices.

**New Feature**: Now operates asynchronously - returns immediately with a 202 status code while processing happens in the background.

### 2. Post-Check API
```http
POST /api/v1/postcheck/{batch_id}
```
Creates a post-change verification check for F5 devices.

**New Feature**: Now operates asynchronously - returns immediately with a 202 status code while processing happens in the background.

### 3. Diff API
```http
GET /api/v1/batch/{batch_id}/diff
```
Gets differences between pre and post-change checks.

**New Feature**: Now provides comprehensive output including:
- All commands executed
- Detailed diffs for each command
- Full pre and post outputs for comparison

### 4. Status API
```http
GET /api/v1/batch/{batch_id}/status
```
Gets status of a batch check operation.

### 5. List Checks API
```http
GET /api/v1/checks
```
Lists and filters check operations.

### 6. Search API
```http
GET /api/v1/search/batches?username={username}
```
Searches for batch operations by username. Returns all batches created by the specified user with detailed information including:
- Batch status
- Device counts
- Precheck and postcheck counts
- Timestamps

### 7. Outputs API
```http
GET /api/v1/batch/{batch_id}/outputs
```
Gets raw command outputs from precheck and postcheck operations for a batch. Supports filtering by:
- Device IP (optional)
- Command (optional)

Returns structured output with:
- Precheck and postcheck status
- Command outputs aligned for easy comparison
- Full command output content

## Connection Management

The application employs an optimized connection management strategy for F5 devices:

- **Connection Pooling**: Maintains persistent connections to F5 devices
- **Session Reuse**: Multiple commands use the same session
- **Automatic Reconnection**: Detects stale connections and re-establishes if needed
- **Resource Cleanup**: Proper connection closure on application shutdown

These improvements significantly reduce overhead from repeatedly establishing connections.

## Updated Architecture

The application now implements asynchronous background processing for improved performance:

- **Non-blocking API Endpoints**: Pre-check and post-check operations return immediately
- **Background Tasks**: Processing continues in the background
- **Improved Database Session Management**: Individual database sessions for each operation
- **Enhanced Error Handling**: Isolated error handling per device

## Example Usage

1. Create a pre-check:
```bash
curl -X POST "http://localhost:8000/api/v1/precheck" \
  -H "Content-Type: application/json" \
  -d '{
    "created_by": "operator",
    "devices": [
      {
        "device_ip": "<DEVICE_IP>",
        "username": "<USERNAME>",
        "password": "<PASSWORD>"
      }
    ],
    "commands": [
      "<COMMAND_1>",
      "<COMMAND_2>"
    ]
  }'
```

Response will now be immediate with a 202 status code:
```json
{
  "batch_id": "123e4567-e89b-12d3-a456-426614174000",
  "checks": [
    {
      "device_ip": "<DEVICE_IP>",
      "precheck_id": null,
      "status": "initiated"
    }
  ],
  "timestamp": "2023-03-31T12:00:00.000000",
  "message": "PreCheck initiated successfully (processing in background)"
}
```

2. Create a post-check:
```bash
curl -X POST "http://localhost:8000/api/v1/postcheck/{batch_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "created_by": "operator",
    "devices": [
      {
        "device_ip": "<DEVICE_IP>",
        "username": "<USERNAME>",
        "password": "<PASSWORD>"
      }
    ]
  }'
```

3. Get the enhanced diff:
```bash
curl "http://localhost:8000/api/v1/batch/{batch_id}/diff"
```

Response now includes comprehensive information:
```json
{
  "batch_id": "123e4567-e89b-12d3-a456-426614174000",
  "devices": [
    {
      "device_ip": "<DEVICE_IP>",
      "precheck_id": "123e4567-e89b-12d3-a456-426614174001",
      "postcheck_id": "123e4567-e89b-12d3-a456-426614174002",
      "status": "completed",
      "summary": {
        "total_commands": 2,
        "commands_with_changes": 1,
        "timestamp": "2023-03-31T12:05:00.000000",
        "diff": { /* Diffs for each command */ }
      },
      "all_commands": [
        {
          "command": "<COMMAND_1>",
          "has_changes": true,
          "diff": [ /* Detailed diff lines */ ],
          "pre_output": "Output before changes",
          "post_output": "Output after changes"
        },
        {
          "command": "<COMMAND_2>",
          "has_changes": false,
          "diff": [],
          "pre_output": "Output with no changes",
          "post_output": "Output with no changes"
        }
      ]
    }
  ],
  "overall_status": "completed"
}
```

4. Search for batches by username:
```bash
curl "http://localhost:8000/api/v1/search/batches?username=operator"
```

Response includes all batches created by the specified user:
```json
{
  "username": "operator",
  "total_batches": 2,
  "batches": [
    {
      "batch_id": "123e4567-e89b-12d3-a456-426614174000",
      "created_at": "2023-03-31T12:00:00.000000",
      "status": "completed",
      "total_devices": 3,
      "completed_devices": 3,
      "precheck_count": 3,
      "postcheck_count": 3
    },
    {
      "batch_id": "123e4567-e89b-12d3-a456-426614174002",
      "created_at": "2023-03-30T14:30:00.000000",
      "status": "partial",
      "total_devices": 2,
      "completed_devices": 1,
      "precheck_count": 2,
      "postcheck_count": 1
    }
  ]
}
```

5. Get command outputs for a batch:
```bash
curl "http://localhost:8000/api/v1/batch/{batch_id}/outputs"
```

Response includes full command outputs from both precheck and postcheck:
```json
{
  "batch_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "total_devices": 3,
  "completed_devices": 3,
  "devices": [
    {
      "device_ip": "<DEVICE_IP>",
      "precheck_id": "123e4567-e89b-12d3-a456-426614174001",
      "postcheck_id": "123e4567-e89b-12d3-a456-426614174002",
      "precheck_status": "completed",
      "postcheck_status": "completed",
      "commands": [
        {
          "command": "<COMMAND_1>",
          "pre_output": "Output before changes",
          "post_output": "Output after changes",
          "has_postcheck": true
        },
        {
          "command": "<COMMAND_2>",
          "pre_output": "Output with no changes",
          "post_output": "Output with no changes",
          "has_postcheck": true
        }
      ]
    }
  ]
}
```

You can also filter by device or command:
```bash
curl "http://localhost:8000/api/v1/batch/{batch_id}/outputs?device_ip=<DEVICE_IP>&command=<COMMAND_1>"
```

## Security Considerations

⚠️ **Important Security Notes:**
- Never commit credentials or sensitive data to version control
- Use environment variables for sensitive configuration
- Implement proper authentication in production
- Use HTTPS in production environments
- Regularly update dependencies for security patches
- Follow your organization's security policies for F5 device access

### Command Security

The API enforces the following security controls:

- **Read-only Commands Only**: The system validates that all commands sent to F5 devices are read-only commands, specifically:
  - `show` commands
  - `tmsh` commands 
  - `cat` commands
  - `list` commands
  - `display` commands
- **Command Validation**: Commands are validated at multiple levels (API endpoint and device handler) to prevent execution of potentially destructive commands.
- **Validation Error Reporting**: Clear error messages are returned when invalid commands are detected.

This protection helps prevent accidental or malicious configuration changes to network devices.

## Development

### Running Tests
```bash
poetry run pytest
```

### Code Formatting
```bash
poetry run black .
poetry run isort .
```

### Linting
```bash
poetry run ruff check .
```

### Type Checking
```bash
poetry run mypy .
```

## Project Structure

The project follows a modular structure:
- `f5_prepost_api/core/` - Core functionality including device handlers and connection management
- `f5_prepost_api/api/` - API endpoints and routing
- `f5_prepost_api/models/` - Data models and schemas
- `f5_prepost_api/utils/` - Utility functions
- `f5_prepost_api/database.py` - Database models and session management 