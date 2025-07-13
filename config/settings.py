"""Global settings and constants"""

import os

SETTINGS = {
    "project_path": "/Workspace/Users/prashant.choubey@dpwapps.com/02-AI-SDR-Model/config/",
    "config_file": "config.json",
    "default_model": "databricks-meta-llama-3-3-70b-instruct",
    "max_tokens": 500,
    "temperature": 0.0,
    "required_packages": ["openai>=1.0.0", "pandas>=1.5.0", "mlflow>=2.8.0"]
}

def get_config_path():
    """Get full path to config file"""
    return os.path.join(SETTINGS["project_path"], SETTINGS["config_file"])

# Quick test
def test_settings():
    print("=== Testing Settings ===")
    print(f"✓ Project path: {SETTINGS['project_path']}")
    print(f"✓ Config path: {get_config_path()}")
    print(f"✓ Default model: {SETTINGS['default_model']}")

if __name__ == "__main__":
    test_settings()
