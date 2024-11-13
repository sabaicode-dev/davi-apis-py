import uuid
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from file.api.serializers import FileResponeSerializer, CreateUserSerializer, UpdateFileSerializer, FileQuerySerializer
import os
from utils import file_util
from file.models import File
import file.api.service as service
from pagination.pagination import Pagination
from bson import ObjectId

class FileViewAllApiView(APIView):
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        file_queryset = File.objects.all().order_by("-created_at")
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(file_queryset, request)
        serializer = FileResponeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class FileUploadView(APIView):
    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):
        # Debug: Print the request data to verify its contents
        print("Request data:", request.data)
        
        if 'file' not in request.data:
            return Response({"error": "No file provided in the request."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file extension
        file_extension = file_util.get_file_extension(str(request.data['file']))
        if file_extension not in file_util.ALLOWED_EXTENSIONS_FILE:
            allowed_exts = ', '.join(file_util.ALLOWED_EXTENSIONS_FILE)
            return Response(
                f"Invalid file extension '{file_extension}'. Allowed extensions are: {allowed_exts}.",
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle file upload
        try:
            data = file_util.handle_uploaded_file(request.data['file'])
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Validate and save with serializer
        serializer = CreateUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadImageView(APIView):
    parser_class = (FileUploadParser,)
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        file_extension = file_util.get_file_extension(str(request.data['file']))

        if file_extension.lower() not in (allowed.lower() for allowed in file_util.ALLOWED_EXTENSIONS_IMAGE):
            allowed_exts = ', '.join(file_util.ALLOWED_EXTENSIONS_IMAGE)
            return Response(
                f"Invalid file extension '{file_extension}'. Allowed extensions are: {allowed_exts}.",
                status=status.HTTP_400_BAD_REQUEST
            )

        data = file_util.handle_uploaded_file_image(request.data['file'])
        return Response(data=data, status=status.HTTP_200_OK)


class ViewHeaderView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        filename = kwargs["filename"]
        result = service.load_datasetHeader(filename=filename)
        return Response(result)


class FileViewImageByName(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, filename):
        image_path = os.path.join(file_util.get_file_server_path(), filename)

        if os.path.exists(image_path):
            return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
        else:
            return Response("Image not found", status=status.HTTP_404_NOT_FOUND)


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

    def get(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        file = get_object_or_404(File, uuid=uuid)
        filename = file.filename
        data = service.load_dataset(filename, file=file.file)

        # Prepare data response
        data.update({
            "id": str(file._id),  # Ensure ObjectId is a string
            "created_at": file.created_at,
            "filename": file.filename,
            "size": file.size,
            "uuid": file.uuid,
            "type": file.type,
        })

        records = data.get("data", [])
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(records, request)

        paginated_response = paginator.get_paginated_response(result_page).data
        paginated_response.update({
            "id": str(file._id),
            "headers": list(data.get("header", [])),
            "file": data.get("file", ""),
            "filename": filename,
            "total": data.get("total", None),
        })

        return Response(paginated_response)


class FileDetailsActionView(APIView):
    def put(self, request, *args, **kwargs):
        uuid = kwargs.get("uuid")
        file = get_object_or_404(File, uuid=uuid)

        serializer = UpdateFileSerializer(file, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteFileView(APIView):
    def delete(self, request, *args, **kwargs):
        uuid = kwargs.get('uuid')
        file = get_object_or_404(File, uuid=uuid, is_deleted=False, is_sample=False)

        if service.remove_file(file.filename):
            file.is_deleted = True
            file.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)


class GetAllImagesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        image_folder_path = file_util.get_file_server_path()

        if os.path.exists(image_folder_path):
            image_files = [f for f in os.listdir(image_folder_path) if os.path.isfile(os.path.join(image_folder_path, f))]
            images_data = [
                {
                    "_id": str(uuid.uuid4().hex),
                    "img": f"https://photostad-api.istad.co/api/v1/files/{filename}"
                } for filename in image_files
            ]

            return Response(images_data, status=status.HTTP_200_OK)

        return Response("No Images", status=status.HTTP_404_NOT_FOUND)
