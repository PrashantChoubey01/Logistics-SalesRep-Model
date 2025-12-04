# FastAPI Server for Logistics AI Bot

REST API server that provides email processing endpoints for the frontend application.

## 🚀 Quick Start

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python api_server.py
   ```

   The server will start on `http://localhost:5001`

### Using uvicorn directly:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### Health Check
```
GET /health
```
Returns server health status.

**Response:**
```json
{
  "status": "healthy",
  "orchestrator_initialized": true,
  "timestamp": "2024-12-04T12:00:00"
}
```

### Readiness Check
```
GET /ready
```
Returns readiness status (checks if orchestrator is initialized).

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-12-04T12:00:00"
}
```

### Process Email
```
POST /api/process-email
```

Processes an email through the LangGraph workflow.

**Request Body:**
```json
{
  "sender": "customer@example.com",
  "subject": "Shipping Quote Request",
  "content": "I need a quote for shipping...",
  "thread_id": "demo_thread_20241204_120000"
}
```

**Response:**
```json
{
  "success": true,
  "thread_id": "demo_thread_20241204_120000",
  "workflow_id": "workflow_20241204_120000_123456",
  "result": {
    "workflow_state": {
      "confirmation_response_result": {...},
      "forwarder_assignment_result": {...},
      ...
    }
  },
  "error": null
}
```

**Error Response:**
```json
{
  "success": false,
  "thread_id": "demo_thread_20241204_120000",
  "workflow_id": "unknown",
  "result": {},
  "error": "Error message here"
}
```

## 🔧 Configuration

### CORS
The server is configured to allow all origins by default. In production, update the CORS middleware in `api_server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Port Configuration
Change the port in `api_server.py`:

```python
uvicorn.run(
    "api_server:app",
    host="0.0.0.0",
    port=5001,  # Change this
    reload=True,
    log_level="info"
)
```

## 🏗️ Architecture

The server:
1. Initializes `LangGraphWorkflowOrchestrator` on startup
2. Provides REST API endpoints for email processing
3. Handles errors gracefully and returns structured responses
4. Maintains CORS configuration for frontend access

## 📝 Notes

- The orchestrator is initialized once on server startup
- All email processing is asynchronous
- Thread IDs are preserved across requests
- Error handling ensures the server never crashes on invalid requests

## 🐛 Troubleshooting

### Orchestrator Not Initialized
- Check server logs for initialization errors
- Ensure all dependencies are installed
- Verify environment variables (API keys, etc.)

### Port Already in Use
- Change the port in `api_server.py`
- Or kill the process using the port:
  ```bash
  # Find process
  lsof -i :8000
  # Kill process
  kill -9 <PID>
  ```

### CORS Issues
- Ensure CORS middleware is configured
- Check that frontend URL matches allowed origins
- Verify request headers are correct

