import requests
import pandas as pd
from bs4 import BeautifulSoup
import uuid
import os
from dotenv import load_dotenv
from file.models import File
from django.forms.models import model_to_dict
import csv
import chardet
from bson import ObjectId
from project.models import Project

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")


def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension

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

def detect_delimiter(file_path):
    with open(file_path, 'r') as file:
        sample = file.read(1024)  # Read a sample of the file
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter

def remove_file(filename):
    path_file = file_server_path_file+filename
    if find_file_by_filename(filename):
        os.remove(path_file)
        return True
    return False


def find_file_by_filename(filename):
    files = os.listdir(file_server_path_file)
    for file in files:
        if file == filename:
            return True
    return False


def get_file_size(filename):
    """ Returns the size of the file in bytes. """
    try:
        # Check if the file exists
        if os.path.isfile(file_server_path_file+filename):
            # Get file size in bytes
            size = os.path.getsize(file_server_path_file+filename)
            return size
        else:
            return "File does not exist"
    except Exception as e:
        return f"Error occurred: {e}"


def scrape_to_csv(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"

    soup = BeautifulSoup(response.text, 'lxml')
    tag_tables = soup.find_all("table")

    table_names = []

    for i, table in enumerate(tag_tables):
        table_data = []

        for row in table.find_all('tr'):
            row_data = []


            for cell in row.find_all(['td', 'th']):
                row_data.append(cell.text.strip())

            if row_data:
                table_data.append(row_data)

        if table_data:

            df = pd.DataFrame(table_data)

            filename = str(uuid.uuid4().hex) + ".csv"

            df.to_csv(os.path.join(
                file_server_path_file, filename), header=False)
            table_names.append(filename)

    return {
        "filename": table_names,
    }

def remove_file_server(filename):
    path_file = file_server_path_file+filename
    if find_file_by_filename(filename):
        os.remove(path_file)
        return True
    return False


def save_file(list_of_files, project_id=None):
    message = []
    confirmed_files = []  # List to hold confirmed files
    for filename in list_of_files:
        # Save file with the associated project_id
        try:
            project = Project.objects.get(_id=project_id)  # Use _id instead of id
        except Project.DoesNotExist:
            return {"message": f"Project with _id {project_id} does not exist."}

        file = File(
            filename=filename,
            file=filename,
            size=get_file_size(filename),
            type=str(get_file_extension(filename)).replace(".", ""),
            project=project  # Associate the file with the project
        )

        # Save file object
        file.save()
        
        # Confirm the file and add it to the confirmed files list
        confirmed_files.append(model_to_dict(file))  # Convert file object to dict

        message.append({
            "message": f"File {filename} has been successfully saved."
        })

    # Return the confirmation for all files that were processed
    return {
        "code": 200,
        "confirmed_message": {"message": "Files successfully confirmed."},
        "confirmed_files": confirmed_files,  # Return the full file details
        "project_id": project_id
    }


def remove_file(list_of_files):
    message_response = []
    for filename in list_of_files:
        message = []
        if find_file_by_filename(filename):
            try:
                remove_file_server(filename)
                message = {"message": f"File {filename} deleted successfully."}
            except Exception as e:
                message = {"message": f"Error occurred while deleting {filename}: {str(e)}"}
        else:
            message = {"message": f"File {filename} not found."}
        
        message_response.append(message)
    return message_response



def load_dataset(filename, size=0):

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
                "total": len(data),
                "header": data.columns.to_list(),
                "data": data.head(int(size)).to_dict(orient='records')
            }
        size = len(data)
        return {
            "total": len(data),
            "header": data.columns.to_list(),
            "data": data.head(int(size)).to_dict(orient='records')
        }
    return None