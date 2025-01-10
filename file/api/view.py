import os
import re
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from bson import ObjectId
from file.models import File
from file.api.serializers import FileResponeSerializer, UpdateFileSerializer, FileQuerySerializer
from project.models import Project
import file.api.service as service
from pagination.pagination import Pagination
from bson import ObjectId
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging
from metafile.api.services.metadata_extractor import MetadataExtractor
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid

# Setup logging
logger = logging.getLogger(__name__)

# View files by project ID
class ProjectFilesView(APIView):
    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        try:
            # Retreve the object
            project = Project.objects.get(_id=ObjectId(project_id))
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        files = project.files.all()
        serializer = FileResponeSerializer(files, many=True)
        print("Response data:",serializer.data)
        return Response(
            {
                "success": True,
                "message": "Files retrieved successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


# View all files with pagination
class FileViewAllApiView(APIView):
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        file_queryset = File.objects.all().order_by("-created_at")
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(file_queryset, request)
        serializer = FileResponeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

from utils.file_util import file_server_path_file
from metafile.api.services.file_loader import FileHandler
from metafile.api.service import MetadataService
from metafile.api.services.data_cleaning import replace_nan_with_none

class FileUploadView(APIView):
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

            # Print the filename
            print("Filename received:::", uploaded_file.name)

            # Use the original filename, no need to add UUID or change the filename
            file_path = os.path.join(file_server_path_file, uploaded_file.name)

            print("File path:::", file_path)
            with open(file_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Determine file type
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            file_type = self.get_file_type(file_extension)

            # Prepare data for the serializer
            data = {
                "filename": uploaded_file.name,
                "file": os.path.basename(file_path),  # Store just the filename, not the full path
                "size": uploaded_file.size,
                "type": file_type,
                "project": project_id,
            }

            # Serialize and save file data
            serializer = FileResponeSerializer(data=data)
            if serializer.is_valid():
                saved_file = serializer.save()
                response_data = FileResponeSerializer(saved_file).data

                # Handle metadata generation and storage
                metadata_result = self.generate_and_store_metadata(
                    file_path=file_path,
                    file_id=response_data["_id"],
                    project_id=project_id
                )
                response_data.update(metadata_result)

                return Response({
                    "success": True,
                    "message": "File uploaded successfully.",
                    "data": response_data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def generate_and_store_metadata(self, file_path, file_id, project_id):
        """
        Generate metadata for the file and store it in the database.
        """
        try:
            # Ensure the file path is valid
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            print(f"Processing file at path: {file_path}")

            # Load the dataset directly from the file path
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path, chunksize=1000)  # Use chunksize if needed
            elif file_path.endswith('.xlsx'):
                data = pd.read_excel(file_path, sheet_name=None)  # Load all sheets if applicable
            elif file_path.endswith('.json'):
                data = pd.read_json(file_path, lines=True)  # Handle line-delimited JSON
            elif file_path.endswith('.txt'):
                # Customize handling for .txt files if required
                data = pd.read_csv(file_path, delimiter='\t', chunksize=1000)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")

            print("Dataset loaded successfully for metadata extraction.")

            # Pass the dataset to the MetadataExtractor
            extractor = MetadataExtractor(df_iterator=data)
            metadata = extractor.extract()
            # print("Extracted metadata:", metadata)

            # Clean metadata (replace NaN values with None)
            cleaned_metadata = replace_nan_with_none(metadata)

            # Store metadata
            metadata_service = MetadataService()
            metadata_stored = metadata_service.store_metadata(
                file_id=file_id,
                project_id=project_id,
                metadata=cleaned_metadata
            )
            print("Metadata stored successfully with ID:", metadata_stored)

            return {
                "metadata_stored": bool(metadata_stored),
                "metadata_id": metadata_stored
            }

        except FileNotFoundError as fnf_error:
            print(f"File not found: {fnf_error}")
            return {"metadata_error": str(fnf_error)}

        except ValueError as value_error:
            print(f"Value error: {value_error}")
            return {"metadata_error": str(value_error)}

        except Exception as e:
            print("Error during metadata generation:", str(e))
            return {"metadata_error": str(e)}

    @staticmethod
    def get_file_type(file_extension):
        file_types = {
            '.csv': 'csv',
            '.txt': 'text',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.pdf': 'pdf'
        }
        return file_types.get(file_extension, 'unknown')

# View file headers
class ViewHeaderView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, *args, **kwargs):
        filename = kwargs["filename"]
        result = service.load_datasetHeader(filename=filename)
        return Response(result)

# Search files by user
class FindFileByUserView(APIView):
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        query_serializer = FileQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        validated_data = query_serializer.validated_data

        filename = validated_data.get("filename")
        type_file = validated_data.get("type")

        file_queryset = File.objects.filter(is_deleted=False, is_sample=False).order_by('-created_at')

        if filename:
            file_queryset = file_queryset.filter(file__icontains=filename)
        if type_file:
            file_queryset = file_queryset.filter(type=type_file)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(file_queryset, request)
        serializer = FileResponeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


# Download a file
class DownloadFileAPIview(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        filename = kwargs.get("filename")

        # Check for files matching the filename, excluding deleted ones
        files = File.objects.filter(filename=filename, is_deleted__in=[False, None])

        if files.exists():
            # If multiple files are found, select the first one (or use other criteria)
            file = files.first()  # You can modify this logic if needed to select based on certain conditions
            
            # Proceed with file download logic
            response = service.download_file(file.filename)
            if response:
                return response

        # If no files are found or something went wrong
        return Response({"message": "File not found or multiple files found."}, status=status.HTTP_404_NOT_FOUND)

# View file details
class FileDetailsViews(APIView):
    pagination_class = Pagination
    permission_classes = [permissions.AllowAny]

    def analyze_columns(self, data):
        """
        Perform comprehensive column analysis
        """
        headers = data.get("header", [])
        records = data.get("data", [])
        
        column_analysis = {}
        for header in headers:
            column_data = [str(row.get(header, '')) for row in records if header in row]
            
            column_analysis[header] = {
                "name": header,
                "total_values": len(column_data),
                "unique_values": len(set(column_data)),
                "unique_percentage": round(len(set(column_data)) / len(column_data) * 100, 2) if column_data else 0,
                "data_types": self.detect_column_types(column_data),
                "sample_values": column_data[:5],  # First 5 sample values
                "is_nullable": any(not value for value in column_data)
            }
        
        return column_analysis

    def detect_column_types(self, column_data):
        """
        Detect potential data types for a column
        """
        data_types = {
            "numeric": 0,
            "string": 0,
            "boolean": 0,
            "date": 0
        }
        
        for value in column_data:
            try:
                # Numeric check
                float(value)
                data_types["numeric"] += 1
            except ValueError:
                # Boolean check
                if value.lower() in ['true', 'false', '0', '1']:
                    data_types["boolean"] += 1
                # Date check (basic)
                elif self.is_date(value):
                    data_types["date"] += 1
                # String (default)
                else:
                    data_types["string"] += 1
        
        # Convert to percentages
        total = len(column_data)
        return {k: round(v/total * 100, 2) for k, v in data_types.items()}

    def is_date(self, value):
        """
        Basic date detection
        """
        date_formats = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{2}/\d{2}/\d{4}$',   # MM/DD/YYYY
            r'^\d{2}-\d{2}-\d{4}$'    # DD-MM-YYYY
        ]
        
        return any(re.match(pattern, str(value)) for pattern in date_formats)

    def get(self, request, *args, **kwargs):
        file_id = kwargs.get("file_id")

        # Validate the file_id format
        if not ObjectId.is_valid(file_id):
            return Response(
                {"error": "Invalid file ID format."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the file by _id
        file = get_object_or_404(File, _id=ObjectId(file_id))

        # Process the file data
        filename = file.filename
        data = service.load_dataset(filename, file=file.file)

        # Analyze columns
        column_analysis = self.analyze_columns(data)

        # Update response data with file details
        data.update({
            "_id": str(file._id),
            "created_at": file.created_at,
            "filename": file.filename,
            "size": file.size,
            "uuid": file.uuid,
            "type": file.type,
        })

        # Paginate the records
        records = data.get("data", [])
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(records, request)


        # Construct paginated response
        paginated_response = paginator.get_paginated_response(result_page).data
        paginated_response.update({
            "_id": str(file._id),
            "headers": list(data.get("header", [])),
            "file": data.get("file", ""),
            "filename": filename,
            "total_row": data.get("total", None),
            "column_analysis": column_analysis,
            "dataset_summary": {
                "total_rows": len(records),
                "total_columns": len(data.get("header", [])),
                "file_type": file.type,
                "file_size": file.size
            }
        })

        return Response(paginated_response)


# Update file details
class FileDetailsActionView(APIView):
    def put(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        file = get_object_or_404(File, uuid=uuid)

        serializer = UpdateFileSerializer(file, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete a file by _id (MongoDB ObjectId)
class DeleteFileView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request, *args, **kwargs):
        file_id = kwargs.get('file_id')

        # Validate the file ID format
        if not ObjectId.is_valid(file_id):
            return Response(
                {"error": "Invalid file ID format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the file by _id from the database
            file = File.objects.filter(_id=ObjectId(file_id)).first()
            if not file:
                logger.error(f"File with ID {file_id} not found in the database.")
                return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

            logger.info(f"Found file: {file.filename} with ID {file._id}")

            # Check if the file is already deleted
            if file.is_deleted:
                return Response({"error": "File has already been deleted."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the file is a sample file (prevent deletion)
            if file.is_sample:
                return Response({"error": "Cannot delete a sample file."}, status=status.HTTP_400_BAD_REQUEST)

            # Proceed with file removal from storage
            if service.remove_file(file.filename):
                logger.info(f"File {file.filename} removed from storage.")
                # Mark the file as deleted in the database (actually delete it)
                self._mark_file_as_deleted(file)
                return Response({"message": "File deleted successfully."}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to delete the file from storage."},
                    status=status.HTTP_404_NOT_FOUND
                )

        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return JsonResponse({"error": f"Error deleting file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def _mark_file_as_deleted(self, file):
        """
        Marks the file as deleted in the database and removes the file record entirely.
        """
        try:
            # Log the attempt to delete the file record from the database
            logger.info(f"Attempting to delete file {file.filename} with _id {file._id} from the database.")
            
            # Delete the file record from the database
            deleted_count, _ = File.objects.filter(_id=file._id).delete()
            
            if deleted_count > 0:
                logger.info(f"File {file.filename} successfully deleted from the database.")
            else:
                logger.warning(f"File {file.filename} not found in the database.")
        except Exception as e:
            logger.error(f"Error deleting file from the database: {str(e)}")
            raise Exception("Error deleting the file from the database.")