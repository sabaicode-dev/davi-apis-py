import csv
from pymongo import MongoClient
from bson import ObjectId
from pymongo.errors import ConnectionFailure, OperationFailure
import pandas as pd
import uuid
import os
from dotenv import load_dotenv
from project.models import Project
from file.models import File
from django.forms.models import model_to_dict
import chardet

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")


# Convert ObjectId to string for JSON serialization
def convert_objectid_to_str(doc):
    if '_id' in doc and isinstance(doc['_id'], ObjectId):
        doc['_id'] = str(doc['_id'])
    return doc

# Load all databases


def get_all_databases(uri: str):
    try:
        client = MongoClient(uri)
        databases = client.list_database_names()
        client.close()
        return databases
    except ConnectionFailure as e:
        return f"Failed to connect to MongoDB: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Load multiple databases and their collections


# def get_multiple_databases(uri: str, database_names: list):
#     try:
#         client = MongoClient(uri)
#         databases_info = {}

#         for db_name in database_names:
#             if db_name not in client.list_database_names():
#                 databases_info[db_name] = {
#                     "error": f"Database '{db_name}' not found."}
#                 continue

#             database = client[db_name]
#             collections = database.list_collection_names()

#             collection_info = {}

#             # Count documents in each collection
#             for collection_name in collections:
#                 collection = database[collection_name]

#                 # Fetch all documents from the collection
#                 documents = collection.find()
#                 documents_list = [convert_objectid_to_str(
#                     doc) for doc in documents]

#                 # Optionally convert to CSV and save to file
#                 filename = collection_name + "_" + \
#                     str(uuid.uuid4().hex) + ".csv"
#                 save_as = file_server_path_file + filename
#                 convert_to_csv_file(documents_list, save_as)

#                 # document_count = collection.count_documents({})
#                 collection_info[collection_name] = filename

#             databases_info[db_name] = collection_info

#         client.close()
#         return databases_info
#     except ConnectionFailure:
#         return {"error": "Failed to connect to MongoDB. Please check the connection URI."}
#     except OperationFailure as e:
#         return {"error": f"MongoDB operation failed: {str(e)}"}
#     except Exception as e:
#         return {"error": f"An error occurred: {str(e)}"}


def get_multiple_databases(uri: str, database_names: list):
    """
    Fetch multiple databases and their collections from MongoDB, and save collections to CSV.
    """
    try:
        client = MongoClient(uri)
        databases_info = {}

        for db_name in database_names:
            if db_name not in client.list_database_names():
                databases_info[db_name] = {
                    "error": f"Database '{db_name}' not found."
                }
                continue

            database = client[db_name]
            collections = database.list_collection_names()

            for collection_name in collections:
                collection = database[collection_name]
                documents = collection.find()
                documents_list = [convert_objectid_to_str(
                    doc) for doc in documents]

                # Generate CSV file for the collection
                filename = f"{collection_name}_{uuid.uuid4().hex}.csv"
                save_as = os.path.join(file_server_path_file, filename)
                convert_to_csv_file(documents_list, save_as)

                # Include the database name in the key
                databases_info[f"{db_name}/{collection_name}"] = filename

        client.close()
        return databases_info
    except ConnectionFailure:
        return {"error": "Failed to connect to MongoDB. Please check the connection URI."}
    except OperationFailure as e:
        return {"error": f"MongoDB operation failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


# Load multiple collections from a specified database


def get_multi_collection(uri: str, database_name: str, collection_names: list):
    try:
        client = MongoClient(uri)
        database = client[database_name]
        collection_data = {}

        for collection_name in collection_names:
            if collection_name not in database.list_collection_names():
                collection_data[collection_name] = {
                    "error": f"Collection '{collection_name}' not found."}
                continue

            collection = database[collection_name]
            documents = collection.find()
            documents_list = [convert_objectid_to_str(
                doc) for doc in documents]

            # Count documents in the collection
            document_count = collection.count_documents({})
            collection_data[collection_name] = {
                "document_count": document_count,
                "documents": documents_list
            }

        client.close()
        return collection_data
    except ConnectionFailure:
        return {"error": "Failed to connect to MongoDB. Please check the connection URI."}
    except OperationFailure as e:
        return {"error": f"MongoDB operation failed: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


# Convert MongoDB documents to a CSV file
def convert_to_csv_file(documents, file_path):
    try:
        # Convert documents to DataFrame
        df = pd.DataFrame(documents)
        # Export to CSV
        df.to_csv(file_path, index=False)
    except Exception as e:
        return str(e)

# comform csv file


def comfirm_csv_to_database():
    try:
        print()
    except Exception as e:
        return str(e)


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


def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension


def find_file_by_filename(filename):
    files = os.listdir(file_server_path_file)
    for file in files:
        if file == filename:
            return True
    return False


def remove_file_server(filename):
    path_file = file_server_path_file+filename
    if find_file_by_filename(filename):
        os.remove(path_file)
        return True
    return False


def save_file(list_of_files, project_id=None):
    message = []
    confirmed_files = []  # List to hold confirmed files

    # Ensure project ID is valid
    if not project_id:
        return {"message": "Project ID is required."}

    # Convert project_id to ObjectId if necessary
    try:
        project_id = ObjectId(project_id)
    except Exception:
        return {"message": f"Invalid Project ID format: {project_id}"}

    # Verify that the project exists
    try:
        # Use _id for MongoDB compatibility
        project = Project.objects.get(_id=project_id)
    except Project.DoesNotExist:
        return {"message": f"Project with _id {project_id} does not exist."}

    # Process and save files
    for filename in list_of_files:
        try:
            # Create a new File object and associate it with the project
            file = File(
                filename=filename,
                file=filename,
                size=get_file_size(filename),
                type=str(get_file_extension(filename)).replace(".", ""),
                project=project  # Associate the file with the project
            )

            # Save file object
            file.save()

            # Add the confirmed file to the list
            confirmed_file_data = model_to_dict(file)
            confirmed_file_data["project"] = str(
                # Convert ObjectId to string
                confirmed_file_data["project"]._id)
            confirmed_files.append(confirmed_file_data)

            message.append({
                "message": f"File {filename} has been successfully saved."
            })

        except Exception as e:
            message.append({
                "message": f"Error occurred while saving file {filename}: {str(e)}"
            })

    # Return the confirmation for all files that were processed
    return {
        "code": 200,
        "confirmed_message": {"message": "Files successfully confirmed."},
        "confirmed_files": confirmed_files,  # Return the full file details
        # Convert ObjectId back to string for response
        "project_id": str(project_id)
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
                message = {"message": f"Error occurred while deleting {
                    filename}: {str(e)}"}
        else:
            message = {"message": f"File {filename} not found."}

        message_response.append(message)
    return message_response


def detect_delimiter(file_path):
    with open(file_path, 'r') as file:
        sample = file.read(1024)  # Read a sample of the file
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter


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
