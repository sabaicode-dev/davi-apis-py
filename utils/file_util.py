import os
import uuid
from dotenv import load_dotenv

dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")

file_base_url = os.getenv("BASE_URL_FILE")
FILE_TEMPLATE_PATH = os.getenv("FILE_TEMPLATE_PATH")

ALLOWED_EXTENSIONS_FILE = ['.csv', '.json', '.txt', '.xlsx']

def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension


def handle_uploaded_file(f):
    original_name = str(f)
    original_extension = get_file_extension(original_name)
    name = original_name.replace(original_extension, "")
    filename = str(uuid.uuid4().hex)+get_file_extension(f.name)
    file_size = f.size
    with open(file_server_path_file + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return {"filename": filename, "size": str(file_size), "file": original_name, "type": get_file_extension(f.name).replace(".", "")}


def find_file_by_filename(filename):
    files = os.listdir(file_server_path_file)
    for file in files:
        if file == filename:
            return True
    return False


def find_file_by_name_sourse(filename):
    try:
        file_state = os.stat(file_server_path_file+filename)
        return file_state
    except FileNotFoundError:
        return None
    

# Handle: boolean detect datatype in column
import pandas as pd
def is_boolean_column(series):
    """Detect if a column contains boolean-like values."""
    try:
        # Handle already boolean dtype
        if pd.api.types.is_bool_dtype(series):
            return True
            
        # Convert series to string and handle mixed types safely
        str_series = series.dropna().astype(str).str.lower().str.strip()
        
        # Define boolean-like values
        boolean_values = {
            'true', 'false', '1', '0', 'yes', 'no', 
            't', 'f', 'y', 'n', 'true.', 'false.',
            'True', 'False',True,False
        }
        
        # Check unique values
        unique_vals = set(str_series.unique())
        
        # Only consider it boolean if all values match boolean patterns
        # and there are at least 2 unique values
        return len(unique_vals) >= 1 and unique_vals.issubset(boolean_values)
        
    except Exception:
        return False