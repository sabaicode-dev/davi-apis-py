from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from save_visualize.models import Visualization, Chart
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
        # Fetch visualizations and their related charts
        visualizations = Visualization.objects.prefetch_related('charts').all()
        serializer = VisualizationSerializer(visualizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class VisualizationDetailView(APIView):
    def get(self, request, pk):
        try:
            # Convert the `pk` string into an ObjectId
            visualization = Visualization.objects.prefetch_related('charts').get(id=ObjectId(pk))
            serializer = VisualizationSerializer(visualization)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            # Fetch the existing visualization
            visualization = Visualization.objects.prefetch_related('charts').get(id=ObjectId(pk))
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Update the visualization's name if provided
            if 'name' in request.data:
                visualization.name = request.data['name']
                visualization.save()

            # Add or update charts in the visualization
            charts_data = request.data.get('charts', [])
            for chart_data in charts_data:
                Chart.objects.create(
                    visualization=visualization,
                    chart_type=chart_data.get('chart_type'),
                    chart_image=chart_data.get('chart_image'),
                    description=chart_data.get('description'),
                    selectedColumns=chart_data.get('selectedColumns')
                )

            # Serialize the updated visualization and its charts
            visualization.refresh_from_db()  # Reload the updated data
            serializer = VisualizationSerializer(visualization)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            # Convert the `pk` string into an ObjectId
            visualization = Visualization.objects.get(id=ObjectId(pk))

            # Optionally check if any charts exist before deleting the visualization
            if not visualization.charts.exists():
                visualization.delete()
                return Response({"message": "Visualization deleted successfully"}, status=status.HTTP_200_OK)

            # If charts exist, respond accordingly
            return Response({"error": "Cannot delete visualization with existing charts."}, status=status.HTTP_400_BAD_REQUEST)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VisualizationDeleteView(APIView):
    def delete(self, request, pk):
        try:
            # Convert the `pk` string into an ObjectId
            visualization = Visualization.objects.get(id=ObjectId(pk))
            visualization.delete()
            return Response({"message": "Visualization deleted successfully"}, status=status.HTTP_200_OK)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

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


class ChartDeleteView(APIView):
    def delete(self, request, visualization_id, chart_id):
        try:
            # Fetch the chart to be deleted
            chart = Chart.objects.get(id=ObjectId(chart_id), visualization_id=ObjectId(visualization_id))
            chart.delete()

            # Check if the visualization has any remaining charts
            remaining_charts = Chart.objects.filter(visualization_id=ObjectId(visualization_id))
            if not remaining_charts.exists():
                # If no charts remain, delete the visualization
                Visualization.objects.get(id=ObjectId(visualization_id)).delete()
                return Response({"message": "Chart and its parent visualization deleted successfully."}, status=status.HTTP_200_OK)

            return Response({"message": "Chart deleted successfully."}, status=status.HTTP_200_OK)
        except Chart.DoesNotExist:
            return Response({"error": "Chart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Visualization.DoesNotExist:
            return Response({"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)