# visualization/api/views.py
import os
from venv import logger
from django.http import FileResponse, Http404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from visualization.api.serializers import VisualizationSerializer,FindKPISerializer
from file.models import File
from visualization.api.service import perform_visualize,view_type_dataset,find_KPI_CATEGORY,find_KPI_NUMBER
from django.shortcuts import get_object_or_404
from bson import ObjectId

class VisualizationApiView(APIView):
    
    def post(self, request, *args, **kwargs):
        serializer = VisualizationSerializer(data=request.data)

        if serializer.is_valid():
            
            file_id = serializer.validated_data.get("file_id")  # Using file_id now
            if not ObjectId.is_valid(file_id):
                return Response(
                    {"error": "Invalid file ID format."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            file = get_object_or_404(File, _id=ObjectId(file_id))  # Fetching by file_id
            filename = file.filename
            chart_name = serializer.validated_data.get("chart_name")
            x_axis = serializer.validated_data.get("x_axis")
            y_axis = serializer.validated_data.get("y_axis")
            
            image_path = perform_visualize(filename=filename, chart_name=chart_name, x_axis=x_axis, y_axis=y_axis)

            if image_path:
                return Response(image_path, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "It might be an error with your dataset. Please contact us."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ViewTypeDataset(APIView):
    
    def get(self, request, *args, **kwargs):

        file_id = kwargs.get("file_id")
        # Validate the file_id format
        if not ObjectId.is_valid(file_id):
            return Response(
                {"error": "Invalid file ID format."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        file = get_object_or_404(File, _id=ObjectId(file_id))
        filename = file.filename
        data_type_dataset = view_type_dataset(filename)

        if data_type_dataset:
            return Response({"data":data_type_dataset},status=status.HTTP_200_OK)

        return Response({"message":"It might be problem with your file please check your file or contact us."},status=status.HTTP_400_BAD_REQUEST)
    

class FindKPIView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = FindKPISerializer(data=request.data)
        
        if serializer.is_valid():
            file_id = serializer.validated_data.get("file_id")
            try:
                file = get_object_or_404(File, _id=ObjectId(file_id))
            except Exception as e:
                return Response({"error": f"Invalid ObjectId: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
            filename = file.filename
            fields = serializer.validated_data.get("fields")
            aggregation = serializer.validated_data.get("aggregation")
            chart_name = serializer.validated_data.get("chart_name")
            
            # Log the fields to make sure they are correct
            logger.info(f"Received fields for KPI calculation: {fields}")
            
            result = None
            if serializer.validated_data.get("type_field") == "number":
                result = find_KPI_NUMBER(filename, chart_name, aggregation, fields)
            elif serializer.validated_data.get("type_field") == "category":
                result = find_KPI_CATEGORY(filename, chart_name, aggregation, fields)
            
            if result:
                logger.info(f"KPI result: {result}")
                return Response({"data": result}, status=status.HTTP_200_OK)
            else:
                logger.warning("No result found for the KPI calculation")
                return Response({"message": "It might be a problem with your file. Please check or contact us."}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.error(f"Invalid serializer data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
