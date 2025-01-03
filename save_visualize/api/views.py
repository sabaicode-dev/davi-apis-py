from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from save_visualize.models import Visualization, Chart
from .serializers import VisualizationSerializer, ChartSerializer

class VisualizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        visualizations = Visualization.objects.filter(user=request.user).order_by('-created_at')
        serializer = VisualizationSerializer(visualizations, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        visualization = Visualization.objects.create(user=request.user, name=data.get("name"))
        serializer = VisualizationSerializer(visualization)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VisualizationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            visualization = Visualization.objects.get(pk=pk, user=request.user)
            serializer = VisualizationSerializer(visualization)
            return Response(serializer.data)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            visualization = Visualization.objects.get(pk=pk, user=request.user)
            visualization.delete()
            return Response({"message": "Visualization deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)


class ChartCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, visualization_id):
        try:
            visualization = Visualization.objects.get(pk=visualization_id, user=request.user)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        chart = Chart.objects.create(
            visualization=visualization,
            chart_type=data.get("chart_type"),
            chart_image=data.get("chart_image"),
            description=data.get("description"),
            selected_columns=data.get("selected_columns"),
        )
        serializer = ChartSerializer(chart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        try:
            chart = Chart.objects.get(pk=pk)
            if chart.visualization.user != request.user:
                return Response({"error": "You do not have permission to delete this chart"}, status=status.HTTP_403_FORBIDDEN)
            chart.delete()
            return Response({"message": "Chart deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Chart.DoesNotExist:
            return Response({"error": "Chart not found"}, status=status.HTTP_404_NOT_FOUND)
