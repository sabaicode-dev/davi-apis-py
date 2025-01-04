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
if not os.path.exists(file_server_path_file):
    raise FileNotFoundError(f"Directory {file_server_path_file} does not exist.")


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
    print(F"File path in remove file {path_file}")
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
    path_file = os.path.join(file_server_path_file, filename)
    if os.path.isfile(path_file):  # Use os.path.isfile to ensure it's a file
        os.remove(path_file)
        return True
    else:
        print(f"File not found: {path_file}")
        return False



def save_file(list_of_files, project_id=None):
    message = []
    confirmed_files = []  # List to hold confirmed files

    # Ensure project ID is valid
    if not project_id:
        return {"message": "Project ID is required."}

    try:
        # Retrieve the project using the project_id
        project = Project.objects.get(_id=ObjectId(project_id))
    except Project.DoesNotExist:
        return {"message": f"Project with ID {project_id} does not exist."}
    except Exception as e:
        return {"message": f"Error retrieving project: {str(e)}"}

    # Process each file
    for filename in list_of_files:
        try:
            print(f"Processing file: {filename}")
            file_path = os.path.join(file_server_path_file, filename)

            # Ensure the file exists
            if not os.path.isfile(file_path):
                print(f"File does not exist: {file_path}")
                message.append({"message": f"File {filename} does not exist on the server."})
                continue

            # Create File object
            file = File(
                filename=filename,
                file=filename,
                size=get_file_size(filename),
                type=str(get_file_extension(filename)).replace(".", ""),
                project=project
            )


            # Save file object to database
            file.save()
            print(f"File saved successfully: {file}")

            # Add the saved file details to confirmed_files
            confirmed_file_data = model_to_dict(file)  # Convert to dict for response
            confirmed_files.append(confirmed_file_data)  # Ensure this is appended
            message.append({"message": f"File {filename} has been successfully saved."})
        except Exception as e:
            message.append({"message": f"Error saving file {filename}: {str(e)}"})

    # Ensure we only return confirmed files if there are any
    if confirmed_files:
        return {
            "code": 200,
            "project_id": project_id,
            "confirmed_message": {
                "message": "Files successfully confirmed.",
                "confirmed_files": confirmed_files  # Return saved file details
            },
        }
    else:
        return {
            "code": 400,
            "project_id": project_id,
            "message": "No files were successfully saved.",
            "details": message
        }

def remove_file(list_of_files):
    message_response = []
    for filename in list_of_files:
        try:
            # Find the file record in the database
            file_record = find_file_by_filename(filename)
            if file_record:
                # Remove the file from the server
                remove_file_server(filename)
                
                # Delete the record from the database
                file_record.delete()
                
                message_response.append({"message": f"File '{filename}' deleted successfully from the server and database."})
            else:
                message_response.append({"message": f"File '{filename}' not found in the database."})
        except Exception as e:
            message_response.append({"message": f"Error occurred while deleting '{filename}': {str(e)}"})
    return message_response


def load_dataset(filename, size=0):
    file_path = os.path.join(file_server_path_file, filename)
    type_file = get_file_extension(filename).replace('.', "").strip()
    data = None

    try:
        # Detect encoding for reading the file
        with open(file_path, 'rb') as raw_data:
            result = chardet.detect(raw_data.read(1000))
        encoding = result['encoding']

        # Read the file based on type
        if type_file == 'csv':
            data = pd.read_csv(file_path, encoding=encoding, on_bad_lines="skip")
        elif type_file == 'json':
            data = pd.read_json(file_path, encoding=encoding)
        elif type_file == 'txt':
            data = pd.read_csv(file_path, encoding=encoding, delimiter=detect_delimiter(file_path))
        elif type_file == 'xlsx':
            data = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

    # Process data if successfully loaded
    if data is not None and not data.empty:
        data = data.where(pd.notnull(data), None)
        if size > 0:
            return {
                "total": len(data),
                "header": data.columns.tolist(),
                "data": data.head(size).to_dict(orient="records"),
            }
        return {
            "total": len(data),
            "header": data.columns.tolist(),
            "data": data.to_dict(orient="records"),
        }
    return None
