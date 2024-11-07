from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser


from django.shortcuts import render

import pandas as pd
from django.forms.models import model_to_dict

from cleansing.api import service
from cleansing.api.serializers import MyDataframeSerializer, CreateFileCleansingSerializer, ProcessFileCleansingSerializer
import pandas as pd
from django.http import JsonResponse
import json
import utils.file_util as file_util
from file.models import File
from django.shortcuts import get_object_or_404


def find_file_by_fileUUID(filename):

    file = File.objects.filter(file=filename)

    if file:
        return file
    return None


class FileUploadView(APIView):

    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):

        result = service.handle_uploaded_file_cleansing(
            request.data['file'], kwargs['pk'])
        serilizer = CreateFileCleansingSerializer(data=result)

        if serilizer.is_valid():
            serilizer.save()

            if 'error' in result:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse(data=result, safe=False)
        return Response(serilizer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileUploadFindInncurateDataView(APIView):

    parser_class = (FileUploadParser,)

    def post(self, request, *args, **kwargs):

        if 'file' in request.FILES:

            file = request.FILES['file']
            if file.size == 0:
                return Response({"error": "The uploaded file is empty."}, status=400)

            try:
                data = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                file.seek(0)  # Move to the start of the file
                data = pd.read_csv(
                    file, encoding='ISO-8859-1', on_bad_lines='skip')
            except pd.errors.EmptyDataError:
                return Response({"error": "No columns to parse from file."}, status=400)

            data_json = data.to_dict(orient='records')
            return Response(data_json)
        else:
            return Response({"error": "No file provided."}, status=400)


class ProcessCleaningFile(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):

        serializer = ProcessFileCleansingSerializer(data=request.data)

        data = None
        create_file_serializer = None
        if serializer.is_valid():

            filename = serializer.validated_data.get('filename')
            file = File.objects.filter(filename=filename).first()
            process = serializer.validated_data.get('process')

            if file_util.find_file_by_filename(filename):

                result = service.process_data_cleansing(filename, process)

                if result == None:
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                if result != None:

                    data = {
                        "created_by": serializer.data["created_by"],
                        "is_original": False,
                        "file": file.file,
                        "filename": result["filename"],
                        "size": result["size"],
                        "type": str(file_util.get_file_extension(result["filename"])).replace(".", ""),
                    }

                    create_file_serializer = CreateFileCleansingSerializer(data=data)
                    
                    if create_file_serializer.is_valid():
                        create_file_serializer.save()
                        return Response(create_file_serializer.data, status=status.HTTP_200_OK)
                    return Response(create_file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                if "error" in result:
                    return Response({"message": result,"status":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({"message": result,"status":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"message": "filename  is not found.","status":500}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = {
            "errors": serializer.errors,
            "status": 500  # Replace with your additional object
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class CleansingWithShellScript(APIView):

    parser_class = (FileUploadParser,)

    def get(self, request, *args, **kwargs):

        created_by = kwargs.get("created_by")
        uuid = kwargs.get("uuid")
        file_data = get_object_or_404(
            File, uuid=uuid, created_by=created_by, is_deleted=False)
        filename = file_data.filename
        file = file_util.find_file_by_name_sourse(filename=filename)
        file_extension = file_util.get_file_extension(filename)

        if file == None:
            return Response({
                "message": "Oops! The file you are looking for could not be found.",
                "advice": "Please check the file path or contact support for assistance."
            }, status=status.HTTP_404_NOT_FOUND)

        file_db = File.objects.filter(filename=filename).first()

        data = {
            "filename": filename,
            "file": file_db.file,
            "type": str(file_extension).replace(".", ""),
            "size": file.st_size,
            "created_by": created_by
        }

        serilizer = CreateFileCleansingSerializer(data=data)

        if serilizer.is_valid():

            result = service.cal_shellscript(filename)
            result["filename"] = filename
            result["file"] = file_db.file

            return JsonResponse(result, safe=False)

        return Response(serilizer.errors, status=status.HTTP_400_BAD_REQUEST)


class CleansingTest(APIView):

    parser_class = (FileUploadParser,)

    def get(self, request):

        file = request.FILES['file']

        files = file_util.handle_uploaded_file(file)

        filename = files["filename"]

        result = service.data_cleansing(filename)

        return JsonResponse(result, safe=False)