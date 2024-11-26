from pymongo import MongoClient
from bson import ObjectId
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from cleansing.api.serializers import CreateFileCleansingSerializer, ProcessFileCleansingSerializer
from cleansing.api.service import data_cleansing, process_cleansing
import logging

from file.models import File

logger = logging.getLogger(__name__)


class FileUploadFindInaccurateDataView(APIView):
    """
    Simplified approach to analyze the file for missing rows, duplicates, and outliers.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        file_id = kwargs.get("file_id")

        # MongoDB connection
        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]

        try:
            # Simplified query: Try to find by `_id`, fallback to filename if needed
            file = None
            if file_id:
                try:
                    file = db.files.find_one({"_id": ObjectId(file_id), "is_deleted": False})
                except Exception as e:
                    logger.warning(f"Invalid ObjectId for file_id: {file_id}. Error: {str(e)}")

            if not file:  # Fallback to find the latest file by project_id
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

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            client.close()



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


class ProcessCleaningFile(APIView):
    """
    View for processing file cleansing based on user-selected operations.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ProcessFileCleansingSerializer(data=request.data)

        if serializer.is_valid():
            filename = serializer.validated_data.get("filename")
            process_list = serializer.validated_data.get("process")

            # Use PyMongo to find the file
            client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]
            file = db.files.find_one({"filename": filename})

            if not file:
                return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

            # Convert ObjectId to string for logging
            logger.info(f"Processing file: {convert_object_ids(file)}")

            # Process cleansing operations
            result = process_cleansing(filename, process_list)

            if "error" in result:
                return Response({"error": result["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Save cleansed data back to the database
            cleansed_file_data = {
                "project": file.get("project_id"),
                "filename": result["filename"],
                "file": result["filename"],
                "size": result["size"],
                "type": "csv",
                "is_original": False,
                "original_file": str(file.get("_id")),  # Convert ObjectId to string
            }

            # Insert cleansed file into MongoDB
            inserted_id = db.files.insert_one(cleansed_file_data).inserted_id
            cleansed_file_data["_id"] = str(inserted_id)

            client.close()

            # Convert all ObjectId fields to strings before returning
            cleansed_file_data = convert_object_ids(cleansed_file_data)

            return Response(cleansed_file_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)