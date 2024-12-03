import re
import os
import logging
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from bson import ObjectId
from file.models import File
from file.api.serializers import FileResponeSerializer, UpdateFileSerializer, FileQuerySerializer
from project.models import Project
import file.api.service as service
from pagination.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from bson import ObjectId
from django.db import transaction
from django.http import JsonResponse

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


# Upload a file and associate it with a project
class FileUploadView(APIView):
    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)  # Debugging

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

        # Save the file to the specified directory
        # base_path = os.getenv("FILE_SERVER_PATH_FILE", default="./uploaded_files")
        base_path = os.getenv("FILE_SERVER_PATH_FILE", default="/home/joker/Desktop/DRIVE/1-Bootcampt_program/SabaiCode_Program_Docs/3-Final_Project/davi-apis-py/server/files")

        if not os.path.exists(base_path):
            os.makedirs(base_path)  # Create the directory if it doesn't exist

        # Save the file to disk
        file_path = os.path.join(base_path, uploaded_file.name)
        with open(file_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Determine file type based on the file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        file_type = None
        if file_extension == '.csv':
            file_type = 'csv'
        elif file_extension == '.txt':
            file_type = 'text'
        elif file_extension in ['.jpg', '.jpeg']:
            file_type = 'image'
        elif file_extension == '.png':
            file_type = 'image'
        elif file_extension == '.pdf':
            file_type = 'pdf'
        else:
            file_type = 'unknown'

        # Prepare data for the serializer
        data = {
            "filename": uploaded_file.name,
            "file": os.path.basename(file_path),
            "size": uploaded_file.size,
            "type": file_type,
            "project": project_id,  # Pass the project ID as a string
        }

        # Serialize the data
        serializer = FileResponeSerializer(data=data)
        if serializer.is_valid():
            saved_file = serializer.save()

            # Return the saved file, ensuring MongoDB _id is used instead of id
            response_data = FileResponeSerializer(saved_file).data
            return Response(response_data, status=status.HTTP_201_CREATED)

        print("Validation Errors:", serializer.errors)  # Debugging
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        file_model = get_object_or_404(File, filename=filename, is_deleted=False)

        file = service.download_file(filename)
        if file:
            return file

        return Response({"message": "file not found"}, status=status.HTTP_404_NOT_FOUND)

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
        # Get the file's ObjectId from the URL parameters (file_id)
        file_id = kwargs.get('file_id')

        # Check if file_id is a valid 24-character ObjectId string
        if len(file_id) != 24:
            return JsonResponse({"error": "Invalid ObjectId format. It should be 24 characters long."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Query the file by its _id (MongoDB ObjectId) and other filters
            print(f"Attempting to retrieve file with ID: {file_id}")
            file = File.objects.get(_id=ObjectId(file_id), is_deleted=False, is_sample=False)
            print(f"File retrieved: {file}")
        except File.DoesNotExist:
            print(f"File with ID {file_id} does not exist or has been deleted.")
            return Response({"error": "File not found or already deleted."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log the full exception message for debugging
            print(f"Error retrieving file: {str(e)}")
            return JsonResponse({"error": f"Error retrieving file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with file deletion if valid
        print(f"Attempting to remove file: {file.filename}")
        if service.remove_file(file.filename):
            file.is_deleted = True
            file.save()
            print(f"File {file.filename} successfully deleted.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            print(f"Failed to delete the file: {file.filename}")
            return Response({"error": "File not found in storage or failed to delete from storage."}, status=status.HTTP_404_NOT_FOUND)