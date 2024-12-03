import pandas as pd
import numpy as np
from utils.file_util import get_file_extension, file_server_path_file
import logging
import os
import scipy.stats as stats


logger = logging.getLogger(__name__)
def data_cleansing(filename):
    """
    Analyze the given file for missing rows, duplicates, outliers, and data types.
    """
    file_path = os.path.join(file_server_path_file, filename)

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
    file_path = os.path.join(file_server_path_file, filename)

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
        cleansed_path = os.path.join(file_server_path_file, cleansed_filename)
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



# New code '======================'
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

def detect_advanced_outliers(data, column):
    """
    Advanced multi-method outlier detection
    """
    # IQR Method
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    # Z-Score Method
    z_scores = np.abs(stats.zscore(data[column]))

    # DBSCAN Clustering
    X = data[column].values.reshape(-1, 1)
    X_scaled = StandardScaler().fit_transform(X)
    
    dbscan = DBSCAN(eps=0.5, min_samples=3)
    outlier_labels = dbscan.fit_predict(X_scaled)

    # Combine outlier detection methods
    outliers = data[
        (data[column] < lower_bound) | 
        (data[column] > upper_bound) | 
        (z_scores > 3) | 
        (outlier_labels == -1)
    ]

    return {
        'values': outliers[column].tolist(),
        'count': len(outliers),
        'detection_methods': {
            'iqr_range': f'[{lower_bound}, {upper_bound}]',
            'z_score_threshold': 3,
            'dbscan': 'Enabled'
        }
    }

def data_cleansing(filename):
    """
    Comprehensive data cleansing and analysis
    """
    # Validate file path
    file_path = os.path.join(file_server_path_file, filename)
    if not os.path.exists(file_path):
        return {"error": f"File not found: {filename}"}

    try:
        # Read file based on extension
        extension = get_file_extension(filename)
        data = pd.read_csv(file_path) if extension == '.csv' else pd.read_json(file_path)

        # Replace NaN with None
        data = data.replace({np.nan: None})

        # Detect missing and duplicate rows
        missing_rows = data[data.isnull().any(axis=1)].to_dict(orient='records')
        duplicate_rows = data[data.duplicated()].to_dict(orient='records')

        # Advanced outlier detection for numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        outliers = {
            col: detect_advanced_outliers(data, col) 
            for col in numeric_cols
        }

        # Comprehensive data type analysis
        data_types = {
            col: {
                'dtype': str(data[col].dtype),
                'non_null_count': data[col].count(),
                'null_count': data[col].isnull().sum(),
                'unique_values': data[col].nunique(),
                'sample_values': data[col].dropna().sample(min(5, len(data))).tolist()
            } for col in data.columns
        }

        return {
            'missing_rows': missing_rows,
            'duplicate_rows': duplicate_rows,
            'outliers': outliers,
            'data_types': data_types,
            'summary': {
                'total_rows': len(data),
                'total_missing_rows': len(missing_rows),
                'total_duplicate_rows': len(duplicate_rows),
            }
        }

    except Exception as e:
        logger.error(f"Data cleansing error: {str(e)}", exc_info=True)
        return {"error": str(e)}

def process_cleansing(filename, process_list):
    """
    Process file cleansing based on user-selected operations
    """
    file_path = os.path.join(file_server_path_file, filename)
    
    if not os.path.exists(file_path):
        return {"error": f"File not found: {filename}"}

    try:
        # Load dataset
        data = pd.read_csv(file_path)

        # Apply cleansing processes
        original_row_count = len(data)
        
        if "delete_missing_row" in process_list:
            data = data.dropna()
        
        if "delete_duplicate_row" in process_list:
            data = data.drop_duplicates()

        # Generate cleansed filename
        cleansed_filename = f"cleansed_{filename}"
        cleansed_path = os.path.join(file_server_path_file, cleansed_filename)
        
        # Save cleansed data
        data.to_csv(cleansed_path, index=False)

        return {
            'filename': cleansed_filename,
            'original_row_count': original_row_count,
            'cleansed_row_count': len(data),
            'rows_removed': original_row_count - len(data),
            'message': "Cleansing process completed successfully"
        }

    except Exception as e:
        logger.error(f"Cleansing process error: {str(e)}", exc_info=True)
        return {"error": str(e)}