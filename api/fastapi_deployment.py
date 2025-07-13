"""FastAPI deployment for the email workflow agent"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import mlflow.pyfunc
import pandas as pd
import uvicorn
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Email Workflow Agent API",
    description="AI-powered email classification and extraction for logistics",
    version="1.0.0"
)

# Global model variable
model = None

# Pydantic models for API
class EmailInput(BaseModel):
    email_text: str
    subject: str
    email_id: Optional[str] = None

class BatchEmailInput(BaseModel):
    emails: List[EmailInput]

class EmailResponse(BaseModel):
    email_id: str
    processing_time_seconds: float
    model_version: str
    timestamp: str
    status: str
    classification: Dict[str, Any]
    extraction: Dict[str, Any]
    next_action: Dict[str, Any]
    workflow_steps: List[str]

@app.on_event("startup")
async def load_model():
    """Load the MLflow model on startup"""
    global model
    try:
        # Load latest version of the registered model
        model_name = "email_workflow_agent"
        model_version = "latest"  # or specify version number
        
        model_uri = f"models:/{model_name}/{model_version}"
        model = mlflow.pyfunc.load_model(model_uri)
        
        logger.info(f"✓ Model loaded: {model_name} version {model_version}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        # Fallback: load from run ID if registered model fails
        try:
            # Replace with your actual run ID
            run_id = "YOUR_RUN_ID_HERE"
            model_uri = f"runs:/{run_id}/model"
            model = mlflow.pyfunc.load_model(model_uri)
            logger.info(f"✓ Model loaded from run: {run_id}")
        except Exception as e2:
            logger.error(f"Failed to load model from run: {e2}")
            model = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Email Workflow Agent API",
        "status": "healthy" if model else "model_not_loaded",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "api_status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/predict", response_model=EmailResponse)
async def predict_single_email(email: EmailInput):
    """Process a single email"""
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare input
        input_data = {
            "email_text": email.email_text,
            "subject": email.subject,
            "email_id": email.email_id or f"api_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # Make prediction
        result = model.predict(input_data)
        
        return EmailResponse(**result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/predict/batch")
async def predict_batch_emails(batch: BatchEmailInput):
    """Process multiple emails in batch"""
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare batch input
        batch_data = []
        for i, email in enumerate(batch.emails):
            batch_data.append({
                "email_text": email.email_text,
                "subject": email.subject,
                "email_id": email.email_id or f"batch_{i}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            })
        
        # Convert to DataFrame
        input_df = pd.DataFrame(batch_data)
        
        # Make predictions
        results_df = model.predict(input_df)
        
        # Convert back to list of dicts
        results = results_df.to_dict('records')
        
        return {
            "batch_size": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/model/info")
async def model_info():
    """Get model information"""
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_name": "email_workflow_agent",
        "model_type": "email_classification_extraction",
        "capabilities": [
            "email_classification",
            "shipment_extraction", 
            "workflow_routing"
        ],
        "supported_email_types": [
            "logistics_request",
            "confirmation_reply",
            "forwarder_response", 
            "clarification_reply",
            "non_logistics"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_deployment:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )