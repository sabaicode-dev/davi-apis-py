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
