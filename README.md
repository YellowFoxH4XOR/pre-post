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

### 2. Post-Check API
```http
POST /api/v1/postcheck/{batch_id}
```
Creates a post-change verification check for F5 devices.

### 3. Diff API
```http
GET /api/v1/batch/{batch_id}/diff
```
Gets differences between pre and post-change checks.

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

## Connection Management

The application employs an optimized connection management strategy for F5 devices:

- **Connection Pooling**: Maintains persistent connections to F5 devices
- **Session Reuse**: Multiple commands use the same session
- **Automatic Reconnection**: Detects stale connections and re-establishes if needed
- **Resource Cleanup**: Proper connection closure on application shutdown

These improvements significantly reduce overhead from repeatedly establishing connections.

## Example Usage

1. Create a pre-check:
```bash
curl -X POST "http://localhost:8000/api/v1/precheck" \
  -H "Content-Type: application/json" \
  -d '{
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

2. Create a post-check:
```bash
curl -X POST "http://localhost:8000/api/v1/postcheck/{batch_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "device_ip": "<DEVICE_IP>",
        "username": "<USERNAME>",
        "password": "<PASSWORD>"
      }
    ]
  }'
```

3. Get the diff:
```bash
curl "http://localhost:8000/api/v1/batch/{batch_id}/diff"
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