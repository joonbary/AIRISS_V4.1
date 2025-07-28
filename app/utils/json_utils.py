"""
JSON serialization utilities
"""
import json
import numpy as np
import pandas as pd
from datetime import datetime, date
from decimal import Decimal
from typing import Any


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Convert various Python/Pandas/NumPy objects to JSON serializable format
    """
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict()
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return convert_to_json_serializable(obj.__dict__)
    else:
        return obj


class JSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles various data types
    """
    def default(self, obj):
        return convert_to_json_serializable(obj)