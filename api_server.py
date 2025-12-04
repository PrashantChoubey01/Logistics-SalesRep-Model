#!/usr/bin/env python3
"""
FastAPI Server for Logistics AI Bot
====================================
Provides REST API endpoint for email processing
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langgraph_workflow_orchestrator import LangGraphWorkflowOrchestrator
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SeaRates Logistics AI API",
    description="API for processing logistics emails through LangGraph workflow",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[LangGraphWorkflowOrchestrator] = None


class EmailRequest(BaseModel):
    """Request model for email processing"""
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject")
    content: str = Field(..., description="Email body content")
    thread_id: Optional[str] = Field(None, description="Thread ID (auto-generated if not provided)")


class EmailResponse(BaseModel):
    """Response model for email processing"""
    success: bool
    thread_id: str
    workflow_id: str
    result: Dict[str, Any]
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    logger.info("🚀 Initializing LangGraph Workflow Orchestrator...")
    try:
        orchestrator = LangGraphWorkflowOrchestrator()
        logger.info("✅ Orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "SeaRates Logistics AI API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "ready": "/ready",
            "process_email": "/api/process-email",
            "docs": "/docs"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "orchestrator_initialized": orchestrator is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/process-email", response_model=EmailResponse)
async def process_email(request: EmailRequest):
    """
    Process an email through the LangGraph workflow
    
    Args:
        request: Email request with sender, subject, content, and optional thread_id
        
    Returns:
        EmailResponse with workflow result
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not initialized. Please wait for startup to complete."
        )
    
    try:
        # Prepare email data
        email_data = {
            "sender": request.sender,
            "subject": request.subject,
            "content": request.content,
            "thread_id": request.thread_id
        }
        
        logger.info(f"📧 Processing email from {request.sender} in thread {request.thread_id or 'new'}")
        
        # Process email through workflow
        result = await orchestrator.process_email(email_data)
        
        # Extract workflow state
        workflow_state = result.get('result', {})
        thread_id = workflow_state.get('thread_id', request.thread_id or f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        workflow_id = workflow_state.get('workflow_id', 'unknown')
        
        logger.info(f"✅ Email processed successfully. Thread: {thread_id}, Workflow: {workflow_id}")
        
        return EmailResponse(
            success=True,
            thread_id=thread_id,
            workflow_id=workflow_id,
            result=workflow_state,
            error=None
        )
        
    except Exception as e:
        logger.error(f"❌ Error processing email: {e}", exc_info=True)
        return EmailResponse(
            success=False,
            thread_id=request.thread_id or "unknown",
            workflow_id="unknown",
            result={},
            error=str(e)
        )


if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )

