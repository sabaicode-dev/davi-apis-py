import os
import uuid
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from bson import ObjectId
from file.models import File
from file.api.serializers import FileResponeSerializer
from metafile.api.services.metadata_extractor import MetadataExtractor
from metafile.api.services.file_loader import FileHandler
from metafile.api.service import MetadataService
from utils.file_util import file_server_path_file

class FileUploadView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Debugging: Log request data
            print("Request Data:", request.data)

            # Validate project_id
            project_id = request.data.get('project_id')
            if not project_id:
                return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not ObjectId.is_valid(project_id):
                return Response({"error": "Invalid Project ID format."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate uploaded file
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return Response({"error": "No file provided in the request."}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure the base directory exists
            if not os.path.exists(file_server_path_file):
                os.makedirs(file_server_path_file)

            # Construct a unique filename and save the uploaded file
            filename = f"{uuid.uuid4().hex}{os.path.splitext(uploaded_file.name)[1]}"
            file_path = os.path.join(file_server_path_file, filename)

            print(f"Saving file to: {file_path}")  # Debugging statement

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Prepare data for the serializer
            data = {
                "filename": uploaded_file.name,
                "file": filename,
                "size": uploaded_file.size,
                "type": os.path.splitext(uploaded_file.name)[1].replace(".", ""),
                "project": project_id,
            }

            # Serialize and save file data
            serializer = FileResponeSerializer(data=data)
            if serializer.is_valid():
                saved_file = serializer.save()

                # Handle metadata generation and storage
                metadata_result = self.generate_and_store_metadata(
                    file_path=file_path,
                    file_id=saved_file._id,
                    project_id=project_id
                )
                
                response_data = serializer.data
                response_data.update(metadata_result)

                return Response({
                    "success": True,
                    "message": "File uploaded successfully.",
                    "data": response_data,
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error during file upload: {str(e)}")  # Debugging statement
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_and_store_metadata(self, file_path, file_id, project_id):
        """Generate metadata for the file and store it in the database."""
        try:
            # Initialize FileHandler with the directory
            file_handler = FileHandler(server_path=file_server_path_file)
            
            # Load the dataset from the file using the correct path
            data = file_handler.load_dataset(file_path)

            # Extract metadata from the loaded data
            extractor = MetadataExtractor(df_iterator=data)
            metadata = extractor.extract()

            # Store metadata using MetadataService
            metadata_service = MetadataService()
            metadata_stored = metadata_service.store_metadata(
                file_id=file_id,
                project_id=project_id,
                metadata=metadata,
            )

            return {
                "metadata_stored": bool(metadata_stored),
                "metadata_id": metadata_stored,
            }
        except Exception as e:
            print("Error during metadata generation:", str(e))  # Debugging statement
            return {"metadata_error": str(e)}

class FileHandler:
    ALLOWED_EXTENSIONS_FILE = ['.csv', '.json', '.txt', '.xlsx', '.xls']

    def __init__(self, server_path):
        self.server_path = server_path

    @staticmethod
    def detect_separator(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                return ';' if sample.count(';') > sample.count(',') else ','
        except Exception as e:
            print(f"Error detecting separator: {e}")
            return ','  # Default to comma if detection fails

    def load_dataset(self, file_name, chunksize=1000):
        extension = os.path.splitext(file_name)[1].lower()
        # Ensure the correct path construction for loading files
        file_path = os.path.join(self.server_path, file_name)  # Correctly construct path

        try:
            if extension == '.csv':
                sep = self.detect_separator(file_path)
                reader = pd.read_csv(file_path, chunksize=chunksize, iterator=True, sep=sep)
            elif extension == '.json':
                reader = pd.read_json(file_path, lines=True, chunksize=chunksize)
            elif extension in ['.xls', '.xlsx']:
                reader = pd.read_excel(file_path, chunksize=chunksize, iterator=True)
            else:
                raise ValueError("Unsupported file format")
            
            return reader
        except Exception as e:
            print(f"Error loading dataset: {e}")
            raise e
