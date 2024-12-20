from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser

from django.http import FileResponse
from django.shortcuts import render

from file.api.serializers import FileResponeSerializer, UpdateFileSerializer, FileQuerySerializer
import os
from utils import file_util
import pandas as pd
from file.models import File
from django.shortcuts import get_object_or_404
import file.api.service as service
import json
from django.http import JsonResponse
from django.forms.models import model_to_dict
from scrape.api.service import scrape_to_csv, save_file, remove_file, load_dataset
from scrape.api.serializers import ScrapeDataByUrlSerializer, ConfirmDataSetSerializer
from django.http import Http404
from pagination.pagination import Pagination
from bson import ObjectId

class ScraperDataByUrlView(APIView):
    def post(self, request, *args, **kwargs):
        # Fetch project_id from the URL
        project_id = kwargs.get('project_id')

        # Validate project_id
        if not project_id:
            return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not ObjectId.is_valid(project_id):
            return Response({"error": "Invalid Project ID format."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and process the URL data
        serializer = ScrapeDataByUrlSerializer(data=request.data)
        if serializer.is_valid():
            result = scrape_to_csv(serializer.validated_data.get("url"))
            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ConfirmDataSetView(APIView):
    def post(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        serializer = ConfirmDataSetSerializer(data=request.data)

        if serializer.is_valid():
            confirmed = save_file(serializer.validated_data.get("confirmed_filename"), project_id)
            rejected = remove_file(serializer.validated_data.get("rejected_filename"))

            return Response({
                "code": 200,
                "confirmed_message": confirmed,
                "rejected_message": rejected,
                "project_id": project_id
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewDataSetByFilenameView(APIView):
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        # Load dataset based on the filename parameter
        data = load_dataset(filename=kwargs.get('filename'))
        
        # Check if data is None, meaning file loading might have failed
        if data is None:
            return Response(
                {"detail": "Dataset not found or could not be loaded."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Safely access "data" key, defaulting to an empty list if not present
        records = data.get("data", [])
        
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(records, request)
        
        # Build paginated response and attach additional metadata
        paginated_response = paginator.get_paginated_response(result_page).data
        paginated_response["headers"] = list(data.get("header", []))
        paginated_response["file"] = data.get("file", "")
        paginated_response["total"] = data.get("total", None)
        paginated_response["filename"] = kwargs.get('filename')

        return Response(paginated_response)

