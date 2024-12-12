from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from metafile.api.services.file_loader import FileLoader
from metafile.api.services.metadata_extractor import MetadataExtractor
from metafile.api.model import FileMetadata
from utils.load_env import FILE_LOCAL_SERVER_PATH
from metafile.api.services.data_cleaning import replace_nan_with_none
from metafile.api.services.file_loader import load_file_from_server


class DatasetViews(APIView):
    def post(self, request, *args, **kwargs):
        try:    
            # Ensure the request contains a file
            if 'file' not in request.data:
                return Response({"error": "No file provided"}, status=400)
            
            file = request.data['file']

            # Instantiate the FileLoader to handle file operations
            file_handler = FileLoader(server_path=FILE_LOCAL_SERVER_PATH)

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
            return Response(cleaned_metadata, status=201)

        except KeyError:
            return Response({"error": "No file provided"}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class LoadFileView(APIView):
    def get(self, request, file_id, *args, **kwargs):
        try:
            # Fetch the file path from the server using file_id
            file_path = load_file_from_server(file_id)
            return Response({"file_path": file_path}, status=200)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)


class FileMetadataView(APIView):
    def get(self, request, file_id, *args, **kwargs):
        # Fetch metadata from the database using file_id
        file_metadata = FileMetadata.objects.filter(file_id=file_id).first()
        if file_metadata:
            return Response({
                "file_id": file_metadata.file_id,
                "filename": file_metadata.filename,
                "uploaded_at": file_metadata.uploaded_at,
            })
        return Response({"error": "File metadata not found"}, status=404)