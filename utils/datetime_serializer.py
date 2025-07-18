"""Comprehensive datetime serialization utility for JSON compatibility."""

import json
from datetime import datetime, date, time
from typing import Any, Dict, List, Union
import logging

logger = logging.getLogger(__name__)

class DateTimeSerializer:
    """Handles serialization of datetime objects and other non-JSON-serializable types."""
    
    @staticmethod
    def serialize(obj: Any) -> Any:
        """
        Recursively serialize objects to be JSON-compatible.
        
        Args:
            obj: Any object to serialize
            
        Returns:
            JSON-serializable version of the object
        """
        try:
            # Handle datetime objects
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, date):
                return obj.isoformat()
            elif isinstance(obj, time):
                return obj.isoformat()
            
            # Handle dictionaries
            elif isinstance(obj, dict):
                return {key: DateTimeSerializer.serialize(value) for key, value in obj.items()}
            
            # Handle lists and tuples
            elif isinstance(obj, (list, tuple)):
                return [DateTimeSerializer.serialize(item) for item in obj]
            
            # Handle objects with isoformat method (like pandas Timestamp)
            elif hasattr(obj, 'isoformat') and callable(getattr(obj, 'isoformat')):
                try:
                    return obj.isoformat()
                except Exception as e:
                    logger.warning(f"Failed to call isoformat on {type(obj)}: {e}")
                    return str(obj)
            
            # Handle objects with __dict__ (custom objects)
            elif hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, type(None))):
                try:
                    return DateTimeSerializer.serialize(obj.__dict__)
                except Exception as e:
                    logger.warning(f"Failed to serialize object {type(obj)}: {e}")
                    return str(obj)
            
            # Handle numpy types
            elif str(type(obj)).startswith("<class 'numpy."):
                return obj.item() if hasattr(obj, 'item') else str(obj)
            
            # Handle pandas types
            elif str(type(obj)).startswith("<class 'pandas."):
                return str(obj)
            
            # Handle other datetime-like objects
            elif str(type(obj)).find('datetime') != -1:
                try:
                    return str(obj)
                except Exception as e:
                    logger.warning(f"Failed to serialize datetime-like object {type(obj)}: {e}")
                    return "datetime_object"
            
            # Handle sets
            elif isinstance(obj, set):
                return list(DateTimeSerializer.serialize(item) for item in obj)
            
            # Handle basic types that are already JSON-serializable
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            
            # Fallback for unknown types
            else:
                try:
                    return str(obj)
                except Exception as e:
                    logger.warning(f"Failed to serialize unknown type {type(obj)}: {e}")
                    return f"<{type(obj).__name__}>"
                    
        except Exception as e:
            logger.error(f"Serialization error for {type(obj)}: {e}")
            return f"<serialization_error:{type(obj).__name__}>"
    
    @staticmethod
    def safe_json_dumps(obj: Any, **kwargs) -> str:
        """
        Safely convert object to JSON string with datetime handling.
        
        Args:
            obj: Object to serialize
            **kwargs: Additional arguments for json.dumps
            
        Returns:
            JSON string
        """
        try:
            serialized = DateTimeSerializer.serialize(obj)
            return json.dumps(serialized, **kwargs)
        except Exception as e:
            logger.error(f"JSON serialization failed: {e}")
            # Fallback: try to serialize with error handling
            try:
                return json.dumps({
                    "error": "serialization_failed",
                    "original_type": str(type(obj)),
                    "fallback": str(obj)
                }, **kwargs)
            except:
                return '{"error": "json_serialization_failed"}'
    
    @staticmethod
    def find_datetime_objects(obj: Any, path: str = "") -> List[str]:
        """
        Find all datetime objects in a nested structure for debugging.
        
        Args:
            obj: Object to search
            path: Current path in the object structure
            
        Returns:
            List of paths where datetime objects were found
        """
        datetime_paths = []
        
        try:
            if isinstance(obj, (datetime, date, time)):
                datetime_paths.append(f"{path}: {type(obj).__name__}")
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    datetime_paths.extend(DateTimeSerializer.find_datetime_objects(
                        value, f"{path}.{key}" if path else key
                    ))
            elif isinstance(obj, (list, tuple)):
                for i, item in enumerate(obj):
                    datetime_paths.extend(DateTimeSerializer.find_datetime_objects(
                        item, f"{path}[{i}]" if path else f"[{i}]"
                    ))
            elif hasattr(obj, '__dict__') and not isinstance(obj, (str, int, float, bool, type(None))):
                datetime_paths.extend(DateTimeSerializer.find_datetime_objects(
                    obj.__dict__, f"{path}.__dict__" if path else "__dict__"
                ))
            elif str(type(obj)).find('datetime') != -1:
                datetime_paths.append(f"{path}: {type(obj).__name__}")
                
        except Exception as e:
            logger.warning(f"Error searching for datetime objects at {path}: {e}")
            
        return datetime_paths

# Convenience functions
def serialize_for_json(obj: Any) -> Any:
    """Convenience function for backward compatibility."""
    return DateTimeSerializer.serialize(obj)

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Convenience function for safe JSON serialization."""
    return DateTimeSerializer.safe_json_dumps(obj, **kwargs)

def find_datetime_objects(obj: Any, path: str = "") -> List[str]:
    """Convenience function for finding datetime objects."""
    return DateTimeSerializer.find_datetime_objects(obj, path) 