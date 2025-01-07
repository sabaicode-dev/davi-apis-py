from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from save_visualize.models import Visualization
from .serializers import VisualizationSerializer, ChartSerializer

class VisualizationListCreateView(APIView):
    def post(self, request):
        if request.content_type != "application/json":
            return Response({"error": "Invalid content type, must be application/json"}, status=400)

        serializer = VisualizationSerializer(data=request.data)
        if serializer.is_valid():
            visualization = serializer.save()
            response_serializer = VisualizationSerializer(visualization)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        visualizations = Visualization.objects.all()
        serializer = VisualizationSerializer(visualizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class VisualizationDetailView(APIView):
    def get(self, request, pk):
        try:
            visualization = Visualization.objects.prefetch_related('charts').get(pk=pk)
            serializer = VisualizationSerializer(visualization)
            return Response(serializer.data)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)


class ChartCreateView(APIView):
    def post(self, request, visualization_id):
        try:
            visualization = Visualization.objects.get(pk=visualization_id)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        data['visualization'] = str(visualization.id)  # Pass visualization ID as a string
        serializer = ChartSerializer(data=data)

        if serializer.is_valid():
            chart = serializer.save()
            return Response(ChartSerializer(chart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
