"""Configuration loader with validation"""

import json
import os
from typing import Dict, Any, Optional
from settings import get_config_path

class ConfigLoader:
    """Handles loading and validation of configuration"""
    
    def __init__(self):
        self.config: Optional[Dict[str, Any]] = None
        self.config_path = get_config_path()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, "r") as f:
                self.config = json.load(f)
            
            # Validate required fields
            required_fields = ["api_key", "base_url"]
            missing_fields = [field for field in required_fields if field not in self.config]
            
            if missing_fields:
                raise ValueError(f"Missing required config fields: {missing_fields}")
            
            return self.config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        if self.config is None:
            self.load_config()
        return self.config.get(key, default)
    
    def validate_config(self) -> bool:
        """Validate configuration completeness"""
        if self.config is None:
            return False
        
        required_keys = ["api_key", "base_url"]
        return all(key in self.config and self.config[key] for key in required_keys)

# Global config instance
_config_loader = ConfigLoader()

def get_config() -> Dict[str, Any]:
    """Get global configuration"""
    return _config_loader.load_config()

# Quick test
def test_config_loader():
    print("=== Testing Config Loader ===")
    
    try:
        config = get_config()
        print(f"✓ Config loaded successfully")
        print(f"✓ API key present: {'api_key' in config}")
        print(f"✓ Base URL present: {'base_url' in config}")
        
        loader = ConfigLoader()
        print(f"✓ Config validation: {loader.validate_config()}")
        
    except Exception as e:
        print(f"✗ Config test failed: {e}")

if __name__ == "__main__":
    test_config_loader()
