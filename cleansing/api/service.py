import pandas as pd
import numpy as np
from utils.file_util import get_file_extension, FILE_LOCAL_SERVER_PATH
import logging
import os
import scipy.stats as stats


logger = logging.getLogger(__name__)
def data_cleansing(filename):
    """
    Analyze the given file for missing rows, duplicates, outliers, and data types.
    """
    file_path = os.path.join(FILE_LOCAL_SERVER_PATH, filename)

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {"error": f"File not found: {filename}"}

    extension = get_file_extension(filename)
    try:
        if extension == ".csv":
            data = pd.read_csv(file_path)
        elif extension == ".json":
            data = pd.read_json(file_path)
        else:
            return {"error": "Unsupported file type for cleansing."}

        # Replace NaN with None for JSON compliance
        data = data.replace({np.nan: None})

        # Identify missing rows
        missing_rows = data[data.isnull().any(axis=1)].to_dict(orient="records")

        # Identify duplicate rows
        duplicate_rows = data[data.duplicated()].to_dict(orient="records")

        # Outlier Detection
        numeric_cols = data.select_dtypes(include=[np.number])
        outliers_info = {}

        for col in numeric_cols:
            # IQR-based outlier detection
            Q1 = numeric_cols[col].quantile(0.25)
            Q3 = numeric_cols[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            iqr_outliers = numeric_cols[(numeric_cols[col] < lower_bound) | (numeric_cols[col] > upper_bound)][col]

            # Z-Score-based outlier detection
            z_scores = stats.zscore(numeric_cols[col].dropna())
            z_outliers = numeric_cols[col][(z_scores > 3) | (z_scores < -3)]

            # Combine both methods and remove duplicates
            combined_outliers = pd.concat([iqr_outliers, z_outliers]).drop_duplicates().tolist()

            outliers_info[col] = combined_outliers

        # Data types
        data_types = data.dtypes.apply(str).to_dict()

        return {
            "missing_rows": missing_rows,
            "duplicate_rows": duplicate_rows,
            "outliers": outliers_info,
            "data_types": data_types,
        }
    except Exception as e:
        logger.error(f"Error during data cleansing: {str(e)}")
        return {"error": str(e)}



def process_cleansing(filename, process_list):
    """
    Cleanses the given file based on the specified processes and saves the result as a new file.
    """
    file_path = os.path.join(FILE_LOCAL_SERVER_PATH, filename)

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {"error": f"File not found: {filename}"}

    try:
        # Load the dataset
        data = pd.read_csv(file_path)

        # Process: Remove rows with missing values
        if "delete_missing_row" in process_list:
            data = data.dropna()

        # Process: Drop duplicate rows
        if "delete_duplicate_row" in process_list:
            data = data.drop_duplicates()

        # Save cleansed data to a new file
        cleansed_filename = f"cleansed_{filename}"
        cleansed_path = os.path.join(FILE_LOCAL_SERVER_PATH, cleansed_filename)
        data.to_csv(cleansed_path, index=False)

        logger.info(f"Cleansing completed. Saved to {cleansed_path}")

        # Return details of the cleansed file
        return {
            "filename": cleansed_filename,
            "size": data.shape[0],
            "message": "Cleansing process completed successfully."
        }
    except Exception as e:
        logger.error(f"Error during cleansing process: {str(e)}")
        return {"error": str(e)}