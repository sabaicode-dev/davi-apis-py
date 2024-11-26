import mimetypes
import os
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

        # Retrieve the file storage path from environment variable
        base_path = os.getenv("FILE_SERVER_PATH_FILE", default="./uploaded_files")
        if not os.path.exists(base_path):
            os.makedirs(base_path)  # Create the directory if it doesn't exist

        # Save the file to the specified directory
        file_path = os.path.join(base_path, uploaded_file.name)
        with open(file_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Prepare data for the serializer
        data = {
            "filename": uploaded_file.name,
            "file": os.path.basename(file_path),  # Store only the file name
            "size": uploaded_file.size,
            "type": uploaded_file.content_type,
            "project": project_id,  # Pass the project ID as a string
        }

        serializer = FileResponeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

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


# View file details
class FileDetailsViews(APIView):
    pagination_class = Pagination
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        file_id = kwargs.get("file_id")  # Use file_id instead of uuid

        # Validate the file_id format (must be a valid ObjectId)
        if not ObjectId.is_valid(file_id):
            return Response({"error": "Invalid file ID format."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the file by _id
        file = get_object_or_404(File, _id=ObjectId(file_id))

        # Process the file data
        filename = file.filename
        data = service.load_dataset(filename, file=file.file)

        # Update response data with file details
        data.update({
            "_id": str(file._id),
            "created_at": file.created_at,
            "filename": file.filename,
            "size": file.size,
            "uuid": file.uuid,  # Include uuid for backward compatibility
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
            "total": data.get("total", None),
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


# Delete a file
@method_decorator(csrf_exempt, name='dispatch')
class DeleteFileView(APIView):
    permission_classes = [permissions.AllowAny]  # Ensure the endpoint is accessible
    
    def delete(self, request, *args, **kwargs):
        try:
            # Extract the UUID of the file from the URL
            uuid = kwargs.get('uuid')
            
            # Ensure the file exists and is not marked as deleted
            file = get_object_or_404(File, uuid=uuid, is_deleted=False, is_sample=False)
            
            # Use the service to remove the file from storage
            file_removed = service.remove_file(file.filename)
            
            if file_removed:
                # Mark the file as deleted in the database
                file.is_deleted = True
                file.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Failed to delete the file."}, status=status.HTTP_400_BAD_REQUEST)
        
        except File.DoesNotExist:
            # Handle the case where the file does not exist
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Catch any other unexpected errors
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
