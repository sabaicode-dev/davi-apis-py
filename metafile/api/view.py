from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from bson import ObjectId
import logging
from metafile.api.service import MetadataService
from metafile.api.services.file_loader import FileHandler
from utils.file_util import file_server_path_file
from metafile.api.services.data_cleaning import replace_nan_with_none
from metafile.api.services.metadata_extractor import MetadataExtractor




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

        except KeyError:
            # Handle case where 'file' is not part of the request
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print('error::: ', e)
            # Handle all other exceptions and return the error message
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class MetadataDetailView(APIView):
    def get(self, request, metadata_id):
        if not metadata_id:
            return Response({"error": "Metadata ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not ObjectId.is_valid(metadata_id):
            return Response({"error": "Invalid metadata ID format"}, status=status.HTTP_400_BAD_REQUEST)

        service = MetadataService()
        metadata = service.get_metadata_by_id(metadata_id)
        
        if metadata:
            # No need for serializer if it's already a dict
            return Response(metadata, status=status.HTTP_200_OK)

        return Response({"error": "Metadata not found or deleted"}, status=status.HTTP_404_NOT_FOUND)


class UpdateMetadataDescriptionView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            metadata_id = data.get("metadata_id")
            new_description = data.get("description")

            if not metadata_id or not new_description:
                return Response({"error": "Metadata ID and description are required"}, status=status.HTTP_400_BAD_REQUEST)

            service = MetadataService()
            updated = service.update_metadata_description(metadata_id, new_description)

            if updated:
                return Response({"message": "Metadata description updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Metadata not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
