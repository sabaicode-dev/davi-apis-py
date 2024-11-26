from bson import ObjectId
import pandas as pd
import numpy as np
from utils.file_util import get_file_extension, file_server_path_file


def data_cleansing(filename):
    """
    Analyze the file for inaccuracies (missing rows, duplicate rows, and outliers).
    """
    try:
        file_path = f"{file_server_path_file}{filename}"
        extension = get_file_extension(filename)

        # Load file based on type
        if extension == ".csv":
            data = pd.read_csv(file_path)
        elif extension == ".json":
            data = pd.read_json(file_path, orient="records")
        else:
            return {"error": "Unsupported file type for cleansing."}

        # Identify missing rows
        missing_rows = data[data.isnull().any(axis=1)]

        # Identify duplicate rows
        duplicate_rows = data[data.duplicated()]

        # Identify numeric column outliers
        numeric_cols = data.select_dtypes(include=[np.number])
        outliers_info = {}
        for col in numeric_cols:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = data[(data[col] < lower_bound) | (data[col] > upper_bound)][col]
            outliers_info[col] = outliers.tolist()

        return {
            "missing_rows": missing_rows.to_dict(orient="records"),
            "duplicate_rows": duplicate_rows.to_dict(orient="records"),
            "outliers": outliers_info,
        }
    except Exception as e:
        return {"error": str(e)}


def process_cleansing(filename, process_list):
    """
    Apply cleansing operations on the file.
    """
    try:
        file_path = f"{file_server_path_file}{filename}"
        data = pd.read_csv(file_path)

        # Apply processes
        if "delete_missing_row" in process_list:
            data = data.dropna()
        if "delete_duplicate_row" in process_list:
            data = data.drop_duplicates()

        # Save the cleansed file
        cleansed_filename = f"cleansed_{filename}"
        cleansed_path = f"{file_server_path_file}{cleansed_filename}"
        data.to_csv(cleansed_path, index=False)

        return {"filename": cleansed_filename, "size": data.shape[0]}
    except Exception as e:
        return {"error": str(e)}
