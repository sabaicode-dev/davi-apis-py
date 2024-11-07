import os
import uuid
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import chardet
import utils.file_util as util
from rest_framework import status
import csv
import subprocess
import json
import os
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")
file_base_url = os.getenv("BASE_URL_FILE")

ALLOWED_EXTENSIONS_FILE = ['.csv', '.json', '.txt', '.xlsx']

PROCESS_CHOICES = (
    ('delete_missing_row', 'Delete Missing Row'),
    ('delete_duplicate_row', 'Delete Duplicate Row'),
    ('data_type_conversion', 'Data type conversion'),
    ('delete_row_outlier', 'Delete Row Outlier'),
    ('impute_by_mean','Impute By Mean'),
    ('impute_by_mode','Impute By Mode'),
    ('remove_missing_cell', 'Remove Missing Cell'),
)


def detect_delimiter(file_path):
    with open(file_path, 'r') as file:
        sample = file.read(1024)  # Read a sample of the file
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter


def data_cleansing(filename):

    file_path = file_server_path_file+filename
    type_file = get_file_extension(filename).replace('.', "").strip()
    try:

        with open(file_path, 'rb') as raw_data:
            result = chardet.detect(raw_data.read(1000))
        encoding = result['encoding']

        data = None

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

        data = data.where(pd.notnull(data), None)

        missing_rows = data.loc[data.isnull().all(axis=1)]
        duplicate_rows = data[data.duplicated()]

        numeric_columns = data.select_dtypes(
            include=['int64', 'float64']).columns

        outliers_info = {}

        for col in numeric_columns:

            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)

            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outlier_values = data[(data[col] < lower_bound) | (
                data[col] > upper_bound)][col]
            outlier_values = outlier_values.apply(
                lambda x: None if abs(x) > 1e308 else x)

            outliers_info[col] = {
                'column_name': col,
                'outlier_range': (lower_bound, upper_bound),
                'outliers': [{'value': value} for value in outlier_values]
            }

        missing_rows_dict = missing_rows.to_dict(orient='records')
        duplicate_rows_dict = duplicate_rows.to_dict(
            orient='records') if not duplicate_rows.empty else {}

        data_types = data.dtypes
        data_types_dict_list = [{'column': idx, 'type': str(
            dtype)} for idx, dtype in data_types.items()]

        return {
            "filename": filename,
            "convert_data_type": data_types_dict_list,
            'missing_rows': missing_rows_dict,
            "duplicate_rows": duplicate_rows_dict,
            "outlier": outliers_info,
        }
    except Exception as e:
        print("error "+str(e))


def process_data_cleansing(filename, process_list):

    script_path = os.path.abspath(
        os.environ.get('PATH_SCRIPT')+'data-cleansing/process_cleansing.sh')
    print(os.environ.get('PATH_SCRIPT')+'data-cleansing/process_cleansing.sh')
# os.environ.get('BASE_URL_FILE')
    if not os.path.isfile(script_path):

        print(f"Script not found at {script_path}")

    else:
        try:
            separator = ", "
            result = subprocess.run(
                ['bash', script_path, filename, separator.join(process_list)], stdout=subprocess.PIPE, text=True
            )
            print(result)
            if result.returncode == 0:

                output = result.stdout
                if not output.__contains__("error hz chento") or not output.__contains__("error message"):

                    result_dict = json.loads(output.replace("'", "\""))
                    return result_dict
                else: 
                    return {
                        "error": "Your file might be lead to some problems. Please check file again such as header or image in file."
                    }
            else:
                # Error
                print("Script error:", result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the shell script: {e}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON output: {e}")
        except Exception as e:
            print(e)


def cal_shellscript(filename):

    script_path = os.path.abspath(
              os.environ.get('PATH_SCRIPT')+'data-cleansing/cleansing_csv.sh')
    print(os.environ.get('PATH_SCRIPT'))
    typefile = get_file_extension(filename).replace(".", "").strip()
    if not os.path.isfile(script_path):

        print(f"Script not found at {script_path}")

    else:
        try:
            result = subprocess.run(
                ['bash', script_path, filename], stdout=subprocess.PIPE, text=True
            )
            print(result)
            if result.returncode == 0:

                output = result.stdout

                if not output.__contains__("error hz chento"):
                    result_dict = json.loads(output.replace("'", "\""))
                    return result_dict
                else:
                    return {
                        "error": "Your file might be lead to some problems. Please check file again such as header or image in file."
                    }
            else:
                # Error
                print("Script error:", result.stderr)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the shell script: {e}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON output: {e}")
        except Exception as e:
            print(e)


def find_outliers_and_ranges(data_column):

    Q1 = data_column.quantile(0.25)
    Q3 = data_column.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outlier_values = data_column[(data_column < lower_bound) | (
        data_column > upper_bound)]
    return {
        'outlier_range': (lower_bound, upper_bound),
        'outliers': [{'index': index, 'value': value} for index, value in outlier_values.items()]
    }


def handle_uploaded_file(f):

    extension = get_file_extension(f.name)

    filename = str(uuid.uuid4().hex) + extension

    with open(file_server_path_file + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return filename


def find_error_data(filename):
    print(filename)


def handle_uploaded_file_cleansing(f, created_by):

    extension = get_file_extension(f.name)
    filename = str(uuid.uuid4().hex) + extension
    file_size = f.size
    file_path = file_server_path_file + filename

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    try:
        # Detect file encoding
        with open(file_path, 'rb') as raw_data:
            result = chardet.detect(raw_data.read(1000))
        encoding = result['encoding']

        # Read file with detected encoding
        try:
            data = pd.read_csv(file_path, encoding=encoding,
                               on_bad_lines='skip')
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, encoding='latin1',
                               on_bad_lines='skip')

        # Replace NaN with None for JSON serialization
        data = data.where(pd.notnull(data), None)

        # Reset the index to convert it to a column and find missing data
        data.reset_index(inplace=True)

        # find missing cell only
       # Find completely missing rows
        missing_rows = data[data.loc[:, data.columns !=
                                     'index'].isnull().all(axis=1)]
        missing_cells = None

        # If there are no completely missing rows, find rows with missing cells
        if missing_rows.empty:
            missing_cells = data[data.isnull().any(axis=1)]
        else:
            missing_cells = pd.DataFrame()  #

        # find missing rows only
        missing_rows = data[data.loc[:, data.columns !=
                                     'index'].isnull().all(axis=1)]

        # find duplicates
        columns_to_check = data.columns[1:]
        duplicate_rows = data[data.duplicated(
            keep=False, subset=columns_to_check)]

        # find outliers if the columnn is numeric
        numeric_columns = data.select_dtypes(
            include=['int64', 'float64', 'number']).columns

        outliers_info = {}

        for col in numeric_columns:
            outliers_info[col] = find_outliers_and_ranges(data[col])

        outliers_info.pop("index")

        # Convert to dictionaries
        missing_cells_dict = missing_cells.to_dict(
            orient='records') if not missing_cells.empty else {}
        missing_rows_dict = missing_rows.to_dict(
            orient='records') if not missing_rows.empty else {}
        duplicate_rows_dict = duplicate_rows.to_dict(
            orient='records') if not duplicate_rows.empty else {}

        data_types = data.dtypes
        data_types_dict_list = [{'column': idx, 'type': str(
            dtype)} for idx, dtype in data_types.items()]

        return {
            "created_by": created_by,
            "filename": filename,
            "size": str(file_size),
            "type": extension.replace('.', ''),
            "column_data_type": data_types_dict_list,
            'missing_cells': missing_cells_dict,
            'missing_rows': missing_rows_dict,
            "duplicate_rows": duplicate_rows_dict,
            "outlier": outliers_info,
        }

    except pd.errors.ParserError as e:
        return {'error': 'Parser error while reading CSV.'}
    except IOError:
        return {'error': 'File not found.'}
    except Exception as e:
        return {'error': str(e)}


# code from here prepare put in shell script

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


def find_file_by_filename(filename):
    files = os.listdir(file_server_path_file)
    for file in files:
        if file == filename:
            return True
    return False


def get_data_frmaes(filename, type):

    df = None
    if type == 'csv':
        df = pd.read_csv(file_server_path_file+filename)
    elif type == 'json':
        df = pd.read_json(file_server_path_file+filename,
                          orient='records', lines=True)
    elif type == 'txt':
        df = pd.read_csv(file_server_path_file+filename,
                         delimiter=get_delimiter(file_server_path_file+filename))
    elif type == 'xlsx':
        df = pd.read_excel(file_server_path_file+filename)
    else:
        print("not in range")
    return df


def process_cleansing(filename, process_list):

    dataframe = None
    extension = get_file_extension(filename)

    if find_file_by_filename(filename):

        type = extension.replace(".", "").lower()
        dataframe = get_data_frmaes(filename, type)

        for process in process_list:

            if process in PROCESS_CHOICES[0]:

                # remove missing row
                dataframe.dropna(inplace=True)

            elif process in PROCESS_CHOICES[1]:
                # remove duplicate row
                dataframe.drop_duplicates(inplace=True)

            elif process in PROCESS_CHOICES[2]:

                # process auto convertion
                dataframe.convert_dtypes().dtypes

            elif process in PROCESS_CHOICES[3]:

                # Remove outliers in numeric columns
                for col in dataframe.select_dtypes(include=['float64', 'int64']).columns:
                    Q1 = dataframe[col].quantile(0.25)
                    Q3 = dataframe[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    dataframe = dataframe[(dataframe[col] >= lower_bound) & (
                        dataframe[col] <= upper_bound)]
        
    result_filename = uuid.uuid4().hex+extension
    dataframe.to_csv(file_server_path_file+result_filename,
                     index=True, header=True)

    return {
        "filename": result_filename,
        "size": dataframe.size,
    }


# till here don't touch