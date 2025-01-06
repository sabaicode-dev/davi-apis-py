from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from save_visualize.models import Visualization, Chart
from .serializers import VisualizationSerializer, ChartSerializer

class VisualizationListCreateView(APIView):
    def post(self, request):
        if request.content_type != "application/json":
            return Response({"error": "Invalid content type, must be application/json"}, status=400)

        serializer = VisualizationSerializer(data=request.data)
        if serializer.is_valid():
            visualization = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        visualizations = Visualization.objects.prefetch_related('charts').all()
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

    def put(self, request, pk):
        try:
            visualization = Visualization.objects.get(pk=pk)
            serializer = VisualizationSerializer(visualization, data=request.data)
            if serializer.is_valid():
                visualization = serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            visualization = Visualization.objects.get(pk=pk)
            visualization.delete()
            return Response({"message": "Visualization deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)


class ChartCreateView(APIView):
    def post(self, request, visualization_id):
        try:
            visualization = Visualization.objects.get(pk=visualization_id)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ChartSerializer(data=request.data)
        if serializer.is_valid():
            chart = serializer.save(visualization=visualization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
