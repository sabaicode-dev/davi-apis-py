import os
import uuid
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import chardet
import utils.file_util as util
from rest_framework import status
import csv
import os
import utils.file_util as file_utile
from django.http import HttpResponse
import re

dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")
file_base_url = os.getenv("BASE_URL_FILE")

def get_delimiter(file_path, num_lines=5):
    try:
        with open(file_path, 'r', newline='') as file:
            # Read a few lines from the text file for analysis
            sample_lines = [file.readline() for _ in range(num_lines)]

            # Use the Sniffer class to detect the delimiter
            dialect = csv.Sniffer().sniff(''.join(sample_lines))

            # The delimiter is stored in the 'delimiter' attribute of the dialect
            return dialect.delimiter
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension


def detect_delimiter(file_path):
    with open(file_path, 'r') as file:
        sample = file.read(1024)  # Read a sample of the file
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter


def load_dataset(filename, size=0,file=None):

    file_path = file_server_path_file+filename
    type_file = get_file_extension(filename).replace('.', "").strip()
    data = None

    try:

        with open(file_path, 'rb') as raw_data:
            result = chardet.detect(raw_data.read(1000))
        encoding = result['encoding']

        if type_file == 'csv':
            try:
                data = pd.read_csv(file_path, encoding=encoding,
                                   on_bad_lines="skip")
            except UnicodeDecodeError:
                data = pd.read_csv(file_path, encoding="latin1",
                                   on_bad_lines="skip")

        elif type_file == 'json':

            try:
                data = pd.read_json(file_path, encoding=encoding)

            except Exception as e:

                print(e)
        elif type_file == 'txt':

            data = pd.read_csv(file_path, encoding=encoding,
                               delimiter=detect_delimiter(file_path))
        elif type_file == 'xlsx':

            data = pd.read_excel(file_path)

    except FileNotFoundError as e:

        print(e)

    if data is not None and not data.empty:

        data = data.where(pd.notnull(data), None)
        data = data.apply(lambda x: x.astype(str) if x.dtype == 'float' else x)
        if int(size) != 0:
            return {
                "file":file,
                "total": len(data),
                "header": data.columns.to_list(),
                "data": data.head(int(size)).to_dict(orient='records')
            }
        size = len(data)
        return {
            "file":file,
            "total": len(data),
            "header": data.columns.to_list(),
            "data": data.head(int(size)).to_dict(orient='records')
        }
    return None

def find_character(text):

    regex_pattern = r'[A-Za-z]'
    matches = re.findall(regex_pattern, text)

    if matches: 
        return True
    return False

def view_type_dataset(filename):

    data = load_dataset(filename)
    if data is not None:
        numeric_columns = []
        object_columns = []

        for column in data.columns:
            original_type = str(data[column].dtype)

            if original_type == 'object':

                numeric_values = data[column].astype(str).str.extract(r'(\d+)', expand=False)
                if not numeric_values.dropna().empty:

                    if find_character(str(data[column].head(1).iloc[0])):
                        object_columns.append(column)
                    else:    
                        numeric_columns.append(column)
                else:
                    object_columns.append(column)
            else:
                numeric_columns.append(column)

        return {
            "count_header": len(data.columns),
            "count_records": len(data),
            "all_columns": data.columns.tolist(),
            "numeric_columns": numeric_columns,
            "object_columns": object_columns
        }
    
    return None

def load_dataset_file(filename):

    file_path = file_server_path_file+filename
    type_file = get_file_extension(filename).replace('.', "").strip()
    data = None

    try:

        with open(file_path, 'rb') as raw_data:
            result = chardet.detect(raw_data.read(1000))
        encoding = result['encoding']

        if type_file == 'csv':
            try:
                data = pd.read_csv(file_path, encoding=encoding,
                                   on_bad_lines="skip")
            except UnicodeDecodeError:
                data = pd.read_csv(file_path, encoding="latin1",
                                   on_bad_lines="skip")

        elif type_file == 'json':

            try:
                data = pd.read_json(file_path, encoding=encoding)

            except Exception as e:

                print(e)
        elif type_file == 'txt':

            data = pd.read_csv(file_path, encoding=encoding,
                               delimiter=detect_delimiter(file_path))
        elif type_file == 'xlsx':

            data = pd.read_excel(file_path)

    except FileNotFoundError as e:

        print(e)

    if data is not None and not data.empty:

        data = data.where(pd.notnull(data), None)
        data = data.apply(lambda x: x.astype(str) if x.dtype == 'float' else x)
        for col in data.columns:
            data.rename(columns={col: str(col).strip()}, inplace=True)

        numeric_columns = view_type_load_dataset(data)["numeric_columns"]
        for col in numeric_columns:
            data[col]= pd.to_numeric(data[col].replace('[^0-9.]', '', regex=True), errors='coerce')
        return data

    return None


def view_type_load_dataset(data):

    if data is not None:
        numeric_columns = []
        object_columns = []

        for column in data.columns:
            original_type = str(data[column].dtype)

            if original_type == 'object':

                numeric_values = data[column].astype(str).str.extract(r'(\d+)', expand=False)
                if not numeric_values.dropna().empty:

                    if find_character(str(data[column].head(1).iloc[0])):
                        object_columns.append(column)
                    else:    
                        numeric_columns.append(column)
                else:
                    object_columns.append(column)
            else:
                numeric_columns.append(column)

        return {
            "count_header": len(data.columns),
            "count_records": len(data),
            "all_columns": data.columns.tolist(),
            "numeric_columns": numeric_columns,
            "object_columns": object_columns
        }
    
    return None



def load_datasetHeader(filename):

    try:
        data = load_dataset_file(filename)
        if data is not None:
            numeric_columns = []
            object_columns = []
            for column in data.columns:
                original_type = str(data[column].dtype)

                if original_type == 'object':

                    numeric_values = data[column].astype(str).str.extract(r'(\d+)', expand=False)
                    if not numeric_values.dropna().empty:

                        if find_character(str(data[column].head(1).iloc[0])):
                            object_columns.append(column)
                        else:    
                            numeric_columns.append(column)
                    else:
                        object_columns.append(column)
                else:
                    numeric_columns.append(column)

            date_columns = []
            for col in data.columns:
                # Check if the column contains string-like data
                if data[col].dtype == 'object' or any(isinstance(x, str) for x in data[col]):
                    try:
                        # Attempt to convert the column to datetime
                        pd.to_datetime(data[col])
                        # If successful, add to the list
                        date_columns.append(col)
                        print(col)
                    except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
                        # If conversion fails, it's not a date column
                        continue
            msg = []
            for col in numeric_columns:
                respone ={
                    "value":col,
                    "label":col
                }
                msg.append(respone)
            return {
                "count_header": len(data.columns),
                "count_records": len(data),
                "header_label":msg,
                "header": data.columns.tolist(),
                "header_numeric": numeric_columns,
                "object_columns": object_columns,
                "header_date": date_columns,  
            }
        
    except Exception as e :
        print(e)
    
    return None

def remove_file(filename):
    path_file = file_server_path_file + filename
    if file_utile.find_file_by_filename(filename):  # Ensure this function returns a valid result
        try:
            os.remove(path_file)  # File removal may raise an exception if the file is locked or missing
            return True
        except OSError as e:
            print(f"Error removing file: {e}")
            return False
    return False
def download_file(filename):

    file_path=file_server_path_file+filename
    if file_utile.find_file_by_filename(filename):

        if os.path.exists(file_path):
        
            with open(file_path, 'rb') as file:
        
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
    
    return None