"""MLflow-tracked workflow agent for model deployment"""

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
DATABRICKS_TOKEN = "dapi81b45be7f09611a410fc3e5104a8cadf-3"
DATABRICKS_BASE_URL = "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"
MODEL_ENDPOINT_ID = "databricks-meta-llama-3-3-70b-instruct"

import os
import sys
import json
import mlflow
import mlflow.pyfunc
import pandas as pd
from typing import Dict, Any, List
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.workflow_agent import ImprovedWorkflowAgent

class MLflowWorkflowModel(mlflow.pyfunc.PythonModel):
    """MLflow wrapper for the workflow agent"""
    
    def __init__(self):
        self.agent = None
        self.model_version = "1.0.0"
        self.model_name = "email_workflow_agent"
    
    def load_context(self, context):
        """Load the workflow agent when model is loaded"""
        self.agent = ImprovedWorkflowAgent()
        self.agent.load_context()
        print(f"✓ MLflow model loaded: {self.model_name} v{self.model_version}")
    
    def predict(self, context, model_input):
        """Process emails through the workflow"""
        if isinstance(model_input, pd.DataFrame):
            # Handle DataFrame input (batch processing)
            results = []
            for _, row in model_input.iterrows():
                input_data = {
                    "email_text": row.get("email_text", ""),
                    "subject": row.get("subject", ""),
                    "email_id": row.get("email_id", str(uuid.uuid4())[:8])
                }
                result = self._process_single_email(input_data)
                results.append(result)
            return pd.DataFrame(results)
        
        elif isinstance(model_input, dict):
            # Handle single email input
            return self._process_single_email(model_input)
        
        else:
            return {"error": "Invalid input format. Expected DataFrame or dict."}
    
    def _process_single_email(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email and log metrics"""
        
        # Add processing metadata
        processing_start = datetime.utcnow()
        email_id = input_data.get("email_id", str(uuid.uuid4())[:8])
        
        # Process through workflow
        result = self.agent.run(input_data)
        
        # Add metadata
        processing_end = datetime.utcnow()
        processing_time = (processing_end - processing_start).total_seconds()
        
        # Enhanced result with metadata
        enhanced_result = {
            "email_id": email_id,
            "processing_time_seconds": processing_time,
            "model_version": self.model_version,
            "timestamp": processing_end.isoformat(),
            **result
        }
        
        # Log metrics to MLflow (if in active run)
        try:
            if mlflow.active_run():
                # Log metrics
                mlflow.log_metric("processing_time", processing_time)
                mlflow.log_metric("confidence", result.get("classification", {}).get("confidence", 0))
                
                # Log classification result
                email_type = result.get("classification", {}).get("email_type", "unknown")
                mlflow.log_metric(f"classification_{email_type}", 1)
                
                # Log extraction success
                extraction = result.get("extraction", {})
                if extraction and not extraction.get("error") and not extraction.get("skipped"):
                    mlflow.log_metric("extraction_success", 1)
                    # Log extraction method
                    method = extraction.get("extraction_method", "unknown")
                    mlflow.log_metric(f"extraction_method_{method}", 1)
                else:
                    mlflow.log_metric("extraction_success", 0)
        
        except Exception as e:
            print(f"Warning: MLflow logging failed: {e}")
        
        return enhanced_result

def train_and_log_model():
    """Train and log the model to MLflow"""
    
    # Set MLflow experiment
    experiment_name = "email_workflow_agent"
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run(run_name=f"workflow_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
        
        # Log parameters
        mlflow.log_param("model_type", "email_workflow_agent")
        mlflow.log_param("llm_model", MODEL_ENDPOINT_ID)
        mlflow.log_param("databricks_endpoint", DATABRICKS_BASE_URL)
        mlflow.log_param("version", "1.0.0")
        
        # Create model instance
        model = MLflowWorkflowModel()
        
        # Test data for validation
        test_data = pd.DataFrame([
            {
                "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th",
                "subject": "Shipping Quote Request",
                "email_id": "test_001"
            },
            {
                "email_text": "Yes, I confirm the booking for the containers",
                "subject": "Re: Booking Confirmation",
                "email_id": "test_002"
            },
            {
                "email_text": "Our rate is $2500 USD for FCL 40ft, valid until month end",
                "subject": "Rate Quote",
                "email_id": "test_003"
            }
        ])
        
        # Log test data as artifact
        test_data.to_csv("test_data.csv", index=False)
        mlflow.log_artifact("test_data.csv")
        
        # Create conda environment
        conda_env = {
            "channels": ["defaults", "conda-forge"],
            "dependencies": [
                "python=3.9",
                "pip",
                {
                    "pip": [
                        "mlflow",
                        "pandas",
                        "openai",
                        "scikit-learn"
                    ]
                }
            ],
            "name": "email_workflow_env"
        }
        
        # Log model
        mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=model,
            conda_env=conda_env,
            registered_model_name="email_workflow_agent"
        )
        
        # Test the logged model
        print("Testing logged model...")
        logged_model = mlflow.pyfunc.load_model("runs:/{}/model".format(mlflow.active_run().info.run_id))
        
        # Test predictions
        predictions = logged_model.predict(test_data)
        print("✓ Model test successful")
        
        # Log test results
        for i, pred in enumerate(predictions.to_dict('records') if isinstance(predictions, pd.DataFrame) else [predictions]):
            mlflow.log_metric(f"test_case_{i+1}_confidence", pred.get("classification", {}).get("confidence", 0))
            mlflow.log_metric(f"test_case_{i+1}_processing_time", pred.get("processing_time_seconds", 0))
        
        print(f"✓ Model logged to MLflow experiment: {experiment_name}")
        print(f"✓ Run ID: {mlflow.active_run().info.run_id}")
        
        return mlflow.active_run().info.run_id

if __name__ == "__main__":
    run_id = train_and_log_model()
    print(f"Model training completed. Run ID: {run_id}")