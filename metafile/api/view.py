# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.views import APIView
# from metafile.api.services.data_cleaning import replace_nan_with_none  # type: ignore
# from metafile.api.services.file_loader import FileHandler
# from metafile.api.services.metadata_extractor import MetadataExtractor  # type: ignore
# from utils.load_env import FILE_LOCAL_SERVER_PATH
        

# class DatasetViews(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Ensure the request contains a file
#             if 'file' not in request.data:
#                 return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
#             file = request.data['file']

#             # Instantiate the FileHandler to handle file operations
#             file_handler = FileHandler(server_path=FILE_LOCAL_SERVER_PATH)

#             # Upload the file to the local server and get the saved file path
#             file_name = file_handler.upload_file_to_server(file=file)

#             # Load the dataset (assuming it's a CSV file)
#             data = file_handler.load_dataset(file_name)

#             # Extract metadata from the data
#             extractor = MetadataExtractor(df_iterator=data)
#             metadata = extractor.extract()

#             # Replace NaN values with None
#             cleaned_metadata = replace_nan_with_none(metadata)

#             # Return the cleaned metadata as the response
#             return Response(cleaned_metadata, status=status.HTTP_201_CREATED)

#         except KeyError:
#             # Handle case where 'file' is not part of the request
#             return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             print('error::: ', e)
#             # Handle all other exceptions and return the error message
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from metafile.api.services.file_loader import FileHandler
from metafile.api.services.metadata_extractor import MetadataExtractor
from metafile.api.services.data_cleaning import replace_nan_with_none
from file.models import File
from utils.load_env import FILE_LOCAL_SERVER_PATH


class DatasetViews(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Ensure the request contains a file and project_id
            if 'file' not in request.data:
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.data['file']
            project_id = request.data.get('project_id')

            # Validate project_id
            if not project_id:
                return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Instantiate the FileHandler to handle file operations
            file_handler = FileHandler(server_path=FILE_LOCAL_SERVER_PATH)

            # Upload the file to the local server and get the saved file path
            file_name = file_handler.upload_file_to_server(file=file)

            # Load the dataset (assuming it's a CSV file)
            data_iterator = file_handler.load_dataset(file_name)

            # Create File object
            file_obj = File.objects.create(
                project_id=project_id,
                filename=file_name,
                type=file_handler.get_file_type(file_name),
                size=file.size,
                # Add other necessary fields
            )

            # Extract metadata
            extractor = MetadataExtractor(df_iterator=data_iterator, file_obj=file_obj)
            metadata_instance = extractor.extract_and_store()

            # Prepare response
            response_data = {
                "file_id": str(file_obj._id),
                "metadata_id": str(metadata_instance._id),
                "filename": file_obj.filename,
                "total_columns": metadata_instance.total_columns,
                "total_rows": metadata_instance.total_rows,
                "columns": metadata_instance.columns
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Comprehensive error handling
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Add a view to retrieve metadata
class MetadataDetailView(APIView):
    def get(self, request, file_id):
        try:
            # Retrieve metadata for a specific file
            metadata = Metadata.objects.get(file_id=file_id)
            
            response_data = {
                "metadata_id": str(metadata._id),
                "file_id": str(metadata.file._id),
                "filename": metadata.file.filename,
                "total_columns": metadata.total_columns,
                "total_rows": metadata.total_rows,
                "columns": metadata.columns,
                "created_at": metadata.created_at
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Metadata.DoesNotExist:
            return Response(
                {"error": "Metadata not found for the given file"}, 
                status=status.HTTP_404_NOT_FOUND
            )