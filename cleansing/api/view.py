from pymongo import MongoClient
from bson import ObjectId
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from cleansing.api.service import process_cleansing
from metafile.api.services.metadata_extractor import MetadataExtractor
from utils.file_util import file_server_path_file
from metafile.api.services.file_loader import FileHandler
from metafile.api.service import MetadataService
from metafile.api.services.data_cleaning import replace_nan_with_none
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


def is_valid_object_id(value):
    """
    Check if a string is a valid MongoDB ObjectId.
    """
    try:
        ObjectId(value)
        return True
    except Exception:
        return False


def serialize_metadata(data):
    """
    Recursively convert ObjectId, datetime, and UUID fields to strings for JSON serialization.
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


def handle_exception(e, logger, message="An unexpected error occurred"):
    """
    Helper function to log and handle exceptions consistently.
    """
    logger.error(f"{message}: {str(e)}")
    return Response({"error": message, "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_file(db, project_id, file_identifier):
    """
    Retrieve a file from the database using multiple identifiers.
    """
    project_id_query = {"project_id": ObjectId(project_id)} if is_valid_object_id(project_id) else {"project_id": project_id}

    if is_valid_object_id(file_identifier):
        file = db.files.find_one({"_id": ObjectId(file_identifier), "is_deleted": False})
        if file:
            return file

    file = db.files.find_one({"filename": file_identifier, "is_deleted": False})
    if file:
        return file

    return db.files.find_one(
        {**project_id_query, "is_deleted": False},
        sort=[("created_at", -1)],
    )


class FileUploadFindInaccurateDataView(APIView):
    """
    API for analyzing a file for missing rows, duplicate rows, and outliers.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        file_identifier = kwargs.get("file_identifier")

        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]

        try:
            file = get_file(db, project_id, file_identifier)
            if not file:
                return Response({"error": "File not found in the database."}, status=status.HTTP_404_NOT_FOUND)

            result = process_cleansing(file["filename"], [
                "analyze_missing_rows",
                "analyze_duplicate_rows",
                "analyze_outliers"
            ])

            if "error" in result:
                return Response(
                    {"error": result["error"], "suggestion": "Ensure the file is valid and has a proper structure."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Add counts to result
            result["missing_rows_count"] = len(result.get("missing_rows", []))
            result["duplicate_rows_count"] = len(result.get("duplicate_rows", []))
            result["outliers_count"] = len(result.get("outliers", {}).get("educ", []))

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return handle_exception(e, logger, "Failed to analyze file for inaccuracies")
        finally:
            client.close()


class ProcessCleaningFile(APIView):
    """
    API for cleaning a file and updating its metadata in the database.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        file_identifier = kwargs.get("file_identifier")

        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]

        try:
            file = get_file(db, project_id, file_identifier)
            if not file:
                return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

            try:
                cleansing_result = process_cleansing(file["filename"], [
                    "delete_missing_row",
                    "delete_duplicate_row"
                ])

                if "error" in cleansing_result:
                    return Response({"error": cleansing_result["error"]}, status=status.HTTP_400_BAD_REQUEST)

                cleansed_file_data = {
                    "project_id": ObjectId(project_id) if is_valid_object_id(project_id) else project_id,
                    "filename": cleansing_result["filename"],
                    "file": cleansing_result["filename"],
                    "size": cleansing_result["size"],
                    "type": "csv",
                    "is_original": False,
                    "original_file": file.get("_id"),
                    "created_at": datetime.utcnow(),
                }

                existing_metadata = db.metadata.find_one({"file_id": file["_id"]})
                if existing_metadata:
                    db.metadata.update_one(
                        {"file_id": file["_id"]},
                        {"$set": {"metadata": cleansed_file_data, "updated_at": datetime.utcnow()}}
                    )
                    metadata_result = {"metadata_updated": True}
                else:
                    inserted_id = db.files.insert_one(cleansed_file_data).inserted_id
                    cleansed_file_data["_id"] = inserted_id
                    metadata_result = cleansed_file_data

                response_data = serialize_metadata(metadata_result)
                response_data["cleansing_message"] = cleansing_result.get("message", "Cleansing completed")

                try:
                    file_handler = FileHandler(server_path=file_server_path_file)
                    data = file_handler.load_dataset(cleansing_result["filename"])

                    extractor = MetadataExtractor(df_iterator=data)
                    metadata = extractor.extract()

                    cleaned_metadata = replace_nan_with_none(metadata)
                    metadata_service = MetadataService()
                    metadata_stored = metadata_service.store_metadata(
                        file_id=str(response_data["_id"]),
                        project_id=project_id,
                        metadata=cleaned_metadata,
                    )

                    response_data["metadata_stored"] = bool(metadata_stored)
                    response_data["metadata_id"] = metadata_stored

                except Exception as metadata_error:
                    logger.error(f"Metadata extraction error: {metadata_error}")
                    response_data["metadata_error"] = str(metadata_error)

                return Response(response_data, status=status.HTTP_200_OK)

            except Exception as cleansing_error:
                return handle_exception(cleansing_error, logger, "Data cleansing failed")

        except Exception as e:
            return handle_exception(e, logger, "Failed to process file")
        finally:
            client.close()
