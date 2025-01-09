from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from bson import ObjectId
import logging
from metafile.api.service import MetadataService
from metafile.api.services.file_loader import FileHandler
from utils.file_util import file_server_path_file
from metafile.api.services.data_cleaning import replace_nan_with_none
from metafile.api.services.metadata_extractor import update_description
from metafile.api.models import Metadata
from pymongo import MongoClient
from django.conf import settings




logger = logging.getLogger(__name__)

def is_valid_object_id(value):
    """Check if a string is a valid MongoDB ObjectId."""
    try:
        ObjectId(value)
        return True
    except Exception:
        return False

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

        except Exception as e:
            logger.error(f"Error in DatasetViews: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MetadataDetailView(APIView):
    def get(self, request, metadata_id):
        if not metadata_id:
            return Response({"error": "Metadata ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not is_valid_object_id(metadata_id):
            return Response({"error": "Invalid metadata ID format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            service = MetadataService()
            metadata = service.get_metadata_by_id(metadata_id)

            if metadata:
                # Return metadata if found
                return Response(metadata, status=status.HTTP_200_OK)

            return Response({"error": "Metadata not found or deleted"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.error(f"Error in MetadataDetailView: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateMetadataDescriptionView(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handle the request to update a column's description.
        """
        try:
            metadata_key = request.data.get("metadata_key")
            new_description = request.data.get("description")

            if not metadata_key:
                return Response({"error": "Metadata key is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not new_description:
                return Response({"error": "Description cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

            # Connect to MongoDB using pymongo
            mongo_uri = settings.DATABASES['default']['CLIENT']['host']
            mongo_db_name = settings.DATABASES['default']['NAME']

            client = MongoClient(mongo_uri)
            db = client[mongo_db_name]

            # Update the description for the specified key
            result = db.metadata.update_one(
                {"metadata.key": metadata_key},  # Find the matching metadata key
                {"$set": {"metadata.$.description": new_description}}  # Update the description
            )

            if result.matched_count == 0:
                return Response({"error": "Key not found in metadata"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Description updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unhandled exception in UpdateMetadataDescriptionView: {e}")
            return Response(
                {"error": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )