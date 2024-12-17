import numpy as np
import pandas as pd


def replace_nan_with_none(obj):
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        else:
            return obj
    elif isinstance(obj, dict):
        return {k: replace_nan_with_none(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_none(elem) for elem in obj]
    else:
        return obj


def is_date_column(series):
    try:
        pd.to_datetime(series.dropna().sample(n=min(100, len(series))))
        return True
    except (ValueError, TypeError):
        return False


def is_date_column(series):
    try:
        date_formats = [
            '%Y-%m-%d', 
            '%m/%d/%Y', 
            '%d-%m-%Y', 
            '%Y/%m/%d',
            '%d/%m/%Y'
        ]
        
        for fmt in date_formats:
            try:
                pd.to_datetime(series.dropna(), format=fmt)
                return True
            except:
                continue
        
        # If no specific format works, try flexible parsing
        pd.to_datetime(series.dropna(), infer_datetime_format=True, errors='raise')
        return True
    except:
        return False