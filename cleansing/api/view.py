from pymongo import MongoClient
from bson import ObjectId
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from cleansing.api.service import data_cleansing, process_cleansing
from metafile.api.services.file_loader import FileHandler
from utils.file_util import file_server_path_file
from metafile.api.services.data_cleaning import replace_nan_with_none
from metafile.api.services.metadata_extractor import MetadataExtractor
from metafile.api.service import MetadataService
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

def convert_object_ids(data):
    """
    Recursively convert ObjectId fields in a dictionary or list to strings.
    """
    if isinstance(data, dict):
        return {k: convert_object_ids(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_object_ids(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data


def serialize_metadata(data):
    """
    Recursively convert ObjectId, datetime, and UUID fields to strings.
    """
    if isinstance(data, dict):
        return {k: serialize_metadata(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_metadata(v) for v in data]
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, uuid.UUID):
        return str(data)
    return data

def is_valid_object_id(value):
    """Check if a string is a valid MongoDB ObjectId."""
    try:
        ObjectId(value)
        return True
    except Exception:
        return False

class FileUploadFindInaccurateDataView(APIView):
    """
    Simplified approach to analyze the file for missing rows, duplicates, and outliers.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        file_identifier = kwargs.get("file_identifier")  # This is the new identifier

        # MongoDB connection
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]

        try:
            file = None

            # Check if file_identifier is a valid ObjectId
            if self.is_valid_object_id(file_identifier):
                print(file_identifier)
                file = db.files.find_one({"_id": ObjectId(file_identifier), "is_deleted": False})

            if not file:  # If not found, fall back to finding by filename
                file = db.files.find_one({"filename": file_identifier, "is_deleted": False})

            if not file:  # Finally fallback to the latest file by project_id
                file = db.files.find_one(
                    {"project_id": project_id, "is_deleted": False},
                    sort=[("created_at", -1)],  # Pick the most recent file
                )

            if not file:
                return Response({"error": "File not found in database."}, status=status.HTTP_404_NOT_FOUND)

            # File found, proceed with cleansing
            result = data_cleansing(file["filename"])

            if "error" in result:
                return Response(
                    {
                        "error": result["error"],
                        "suggestion": "Ensure the file exists and has a valid structure.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract counts for missing rows, duplicate rows, and outliers
            missing_rows_count = len(result.get("missing_rows", []))
            duplicate_rows_count = len(result.get("duplicate_rows", []))
            outliers_count = len(result.get("outliers", {}).get("educ", []))

            # Add the counts to the response result
            result["missing_rows_count"] = missing_rows_count
            result["duplicate_rows_count"] = duplicate_rows_count
            result["outliers_count"] = outliers_count

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            client.close()

    def is_valid_object_id(self, value):
        """Check if a string is a valid MongoDB ObjectId."""
        try:
            ObjectId(value)
            return True
        except Exception:
            return False
        
    def get_file(self, db, project_id, file_identifier):
        """
        Retrieve a file from the database based on multiple identifiers.
        """
        if is_valid_object_id(file_identifier):
            file = db.files.find_one({"_id": ObjectId(file_identifier), "is_deleted": False})
            if file:
                return file

        file = db.files.find_one({"filename": file_identifier, "is_deleted": False})
        if file:
            return file

        return db.files.find_one(
            {"project_id": project_id, "is_deleted": False},
            sort=[("created_at", -1)],
        )
    
class DatasetViews(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Ensure the request contains a file
            if 'file' not in request.data:
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.data['file']

            # Instantiate the FileHandler to handle file operations
            file_handler = FileHandler(server_path=file_server_path_file)

            # Upload the file to the local server and get the saved file path
            file_name = file_handler.upload_file_to_server(file=file)

            # Load the dataset (assuming it's a CSV file)
            data = file_handler.load_dataset(file_name)

            # Extract metadata from the data
            extractor = MetadataExtractor(df_iterator=data)
            metadata = extractor.extract()

            # Replace NaN values with None
            cleaned_metadata = replace_nan_with_none(metadata)

            # Return the cleaned metadata as the response
            return Response(cleaned_metadata, status=status.HTTP_201_CREATED)

        except KeyError:
            # Handle case where 'file' is not part of the request
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print('error::: ', e)
            # Handle all other exceptions and return the error message
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessCleaningFile(APIView):
    def post(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        file_identifier = kwargs.get("file_identifier")

        # MongoDB connection
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]

        response_data = {}  # Initialize response data

        try:
            # Find the file
            file = self._get_file(db, project_id, file_identifier)
            if not file:
                return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

            # Perform data cleansing
            try:
                cleansing_result = process_cleansing(file["filename"], [
                    "delete_missing_row",
                    "delete_duplicate_row"
                ])
                if "error" in cleansing_result:
                    response_data["cleansing_error"] = cleansing_result["error"]
                else:
                    # Prepare cleansed file data
                    cleansed_file_data = {
                        "project_id": project_id,
                        "filename": cleansing_result["filename"],
                        "file": cleansing_result["filename"],
                        "size": cleansing_result["size"],
                        "type": "csv",
                        "is_original": False,
                        "original_file": str(file.get("_id")),
                        "created_at": datetime.utcnow()
                    }
                    # Insert cleansed file into MongoDB
                    inserted_id = db.files.insert_one(cleansed_file_data).inserted_id
                    cleansed_file_data["_id"] = str(inserted_id)

                    response_data.update(cleansed_file_data)
                    response_data["cleansing_message"] = cleansing_result.get("message", "Cleansing completed")
            except Exception as cleansing_error:
                response_data["cleansing_error"] = str(cleansing_error)

            # Correct the file path when loading the dataset
            try:
                if "cleansing_error" not in response_data:
                    file_handler = FileHandler(server_path=file_server_path_file)
                    cleansed_file_path = f"{cleansing_result['filename']}"  # Fix path here
                    data = file_handler.load_dataset(cleansed_file_path)

                    # Extract metadata
                    extractor = MetadataExtractor(df_iterator=data)
                    metadata = extractor.extract()

                    # Clean metadata
                    cleaned_metadata = replace_nan_with_none(metadata)

                    # Store metadata
                    metadata_service = MetadataService()
                    metadata_stored = metadata_service.store_metadata(
                        file_id=response_data["_id"],
                        project_id=project_id,
                        metadata=cleaned_metadata
                    )

                    response_data["metadata_stored"] = bool(metadata_stored)
                    response_data["metadata_id"] = metadata_stored
            except Exception as metadata_error:
                response_data["metadata_error"] = str(metadata_error)

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            client.close()

    def _get_file(self, db, project_id, file_identifier):
        """
        Retrieve a file from the database based on multiple identifiers.
        """
        if is_valid_object_id(file_identifier):
            file = db.files.find_one({"_id": ObjectId(file_identifier), "is_deleted": False})
            if file:
                return file

        file = db.files.find_one({"filename": file_identifier, "is_deleted": False})
        if file:
            return file

        return db.files.find_one(
            {"project_id": project_id, "is_deleted": False},
            sort=[("created_at", -1)],
        )