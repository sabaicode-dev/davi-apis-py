# visualization/api/views.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.forms.models import model_to_dict
from visualization.api.serializers import VisualizationSerializer,FindKPISerializer
from file.models import File
from visualization.api.service import perform_visualize,view_type_dataset,find_KPI_CATEGORY,find_KPI_NUMBER
from django.shortcuts import get_object_or_404

class VisualizationApiView(APIView):
    
    def post(self, request):

        serializer = VisualizationSerializer(data=request.data)

        if serializer.is_valid():
            
            file_uuid = serializer.validated_data.get("file_uuid")
            file = get_object_or_404(File,uuid=file_uuid,is_deleted=False)
            filename = file.filename
            chart_name = serializer.validated_data.get("chart_name")
            x_axis = serializer.validated_data.get("x_axis")
            y_axis = serializer.validated_data.get("y_axis")
            
            image_path = perform_visualize(filename = filename, chart_name = chart_name, x_axis =x_axis, y_axis= y_axis)

            if image_path:
                return Response(image_path, status=status.HTTP_200_OK)

            else:
                return Response(
                        {"message": "It mighe be error with your dataset. Please contact us."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewTypeDataset(APIView):
    
    def get(self, request, *args, **kwargs):

        uuid = kwargs.get("uuid_file")
        file = get_object_or_404(File,uuid=uuid,is_deleted=False)
        filename = file.filename
        data_type_dataset = view_type_dataset(filename)

        if data_type_dataset:
            return Response({"data":data_type_dataset},status=status.HTTP_200_OK)

        return Response({"message":"It might be problem with your file please check your file or contact us."},status=status.HTTP_400_BAD_REQUEST)
    


class FindKPIView(APIView):

    def post(self, request, *args, **kwargs):

        serilizer  = FindKPISerializer(data=request.data)
        if serilizer.is_valid():
            
            uuid = serilizer.validated_data.get("file_uuid")
            file = get_object_or_404(File,uuid=uuid,is_deleted=False)
            filename = file.filename
            chart_name = serilizer.validated_data.get("chart_name")
            field= serilizer.validated_data.get("fields")
            aggregation = serilizer.validated_data.get("aggregation")
            result = None

            if serilizer.validated_data.get("type_field") == "number":
                result = find_KPI_NUMBER(filename, chart_name,aggregation,field)

            elif serilizer.validated_data.get("type_field") == "category":
                result = find_KPI_CATEGORY(filename, chart_name,aggregation,field)

            if result != None:
                return Response({"data":result},status=status.HTTP_200_OK)
            return Response({"message":"It might be problem with your file please check your file or contact us."},status=status.HTTP_400_BAD_REQUEST)
    
        return Response(serilizer.errors,status=status.HTTP_400_BAD_REQUEST)