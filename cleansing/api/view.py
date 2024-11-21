from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import pandas as pd
from bson import ObjectId
from cleansing.api import service
from file.models import File
from cleansing.api.serializers import ProcessFileCleansingSerializer, CreateFileCleansingSerializer
from cleansing.api.service import process_cleansing, data_cleansing


class FileUploadFindInncurateDataView(APIView):
    """
    View for uploading a file and analyzing its inaccurate data (missing rows, duplicates, outliers).
    """

    def post(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        file_id = kwargs.get("file_id")

        # Validate project and file existence
        if not ObjectId.is_valid(project_id) or not ObjectId.is_valid(file_id):
            return Response({"error": "Invalid project or file ID format."}, status=status.HTTP_400_BAD_REQUEST)

        file = get_object_or_404(File, _id=ObjectId(file_id), project_id=ObjectId(project_id), is_deleted=False)

        # Perform cleansing analysis
        result = data_cleansing(file.filename)

        if "error" in result:
            return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)


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

            # Verify the file exists
            file = File.objects.filter(filename=filename, is_deleted=False).first()
            if not file:
                return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

            # Process the file with the selected cleansing operations
            result = process_cleansing(filename, process_list)

            if not result:
                return Response({"error": "Cleansing process failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Save the cleansed file data as a new entry in the database
            cleansed_file_data = {
                "project": file.project_id,
                "filename": result["filename"],
                "file": result["filename"],
                "size": result["size"],
                "type": "csv",
                "is_original": False,
                "is_deleted": False,
            }

            create_file_serializer = CreateFileCleansingSerializer(data=cleansed_file_data)
            if create_file_serializer.is_valid():
                create_file_serializer.save()
                return Response(create_file_serializer.data, status=status.HTTP_200_OK)
            return Response(create_file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CleansingWithShellScript(APIView):
    """
    Cleansing file with shell script implementation.
    """

    def get(self, request, *args, **kwargs):
        created_by = kwargs.get("created_by")
        uuid = kwargs.get("uuid")

        # Validate the file exists
        file = get_object_or_404(File, uuid=uuid, created_by=created_by, is_deleted=False)

        # Run shell script cleansing
        result = service.cal_shellscript(file.filename)

        if "error" in result:
            return Response({"error": result["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)


class CleansingTest(APIView):
    """
    Testing cleansing by processing an already uploaded file.
    """

    def post(self, request, *args, **kwargs):
        filename = request.data.get("filename")

        # Check if the file exists in the database
        file = File.objects.filter(filename=filename, is_deleted=False).first()
        if not file:
            return Response({"error": "File not found."}, status=status.HTTP_404_NOT_FOUND)

        # Perform data cleansing
        result = data_cleansing(filename)

        if "error" in result:
            return Response({"error": result["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)

