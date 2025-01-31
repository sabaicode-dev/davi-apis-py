from venv import logger
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from visualization.api.serializers import (
    ChartSerializer,
    RecommendVisualizationSerializer,
    VisualizationSerializer,
    FindKPISerializer,
)
from file.models import File
from visualization.api.service import (
    perform_visualize,
    view_type_dataset,
    find_KPI_CATEGORY,
    find_KPI_NUMBER,
)
from django.shortcuts import get_object_or_404
from bson import ObjectId
from visualization.models import Chart, Visualization


class VisualizationListCreateView(APIView):
    def post(self, request):
        if request.content_type != "application/json":
            return Response(
                {"error": "Invalid content type, must be application/json"}, status=400
            )

        serializer = VisualizationSerializer(data=request.data)
        if serializer.is_valid():
            visualization = serializer.save()
            response_serializer = VisualizationSerializer(visualization)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Fetch visualizations and their related charts
        visualizations = Visualization.objects.prefetch_related("charts").all()
        serializer = VisualizationSerializer(visualizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VisualizationDetailViewUpdateDelete(APIView):
    def get(self, request, pk):
        try:
            # Convert the `pk` string into an ObjectId
            visualization = Visualization.objects.prefetch_related("charts").get(
                id=ObjectId(pk)
            )
            serializer = VisualizationSerializer(visualization)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Visualization.DoesNotExist:
            return Response(
                {"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            # Fetch the existing visualization
            visualization = Visualization.objects.prefetch_related("charts").get(
                id=ObjectId(pk)
            )
        except Visualization.DoesNotExist:
            return Response(
                {"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Update the visualization's name if provided
            if "name" in request.data:
                visualization.name = request.data["name"]
                visualization.save()

            # Add or update charts in the visualization
            charts_data = request.data.get("charts", [])
            for chart_data in charts_data:
                Chart.objects.create(
                    visualization=visualization,
                    chart_type=chart_data.get("chart_type"),
                    chart_image=chart_data.get("chart_image"),
                    description=chart_data.get("description"),
                    selectedColumns=chart_data.get("selectedColumns"),
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
            visualization.delete()
            return Response(
                {"message": "Visualization deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except Visualization.DoesNotExist:
            return Response(
                {"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChartCreateView(APIView):
    def post(self, request, visualization_id):
        try:
            visualization = Visualization.objects.get(pk=visualization_id)
        except Visualization.DoesNotExist:
            return Response(
                {"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data
        data["visualization"] = str(
            visualization.id
        )  # Pass visualization ID as a string
        serializer = ChartSerializer(data=data)

        if serializer.is_valid():
            chart = serializer.save()
            return Response(ChartSerializer(chart).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChartDeleteView(APIView):
    def delete(self, request, visualization_id, chart_id):
        try:
            # Fetch the chart to be deleted
            chart = Chart.objects.get(
                id=ObjectId(chart_id), visualization_id=ObjectId(visualization_id)
            )
            chart.delete()

            # Check if the visualization has any remaining charts
            remaining_charts = Chart.objects.filter(
                visualization_id=ObjectId(visualization_id)
            )
            if not remaining_charts.exists():
                # If no charts remain, delete the visualization
                Visualization.objects.get(id=ObjectId(visualization_id)).delete()
                return Response(
                    {
                        "message": "Chart and its parent visualization deleted successfully."
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {"message": "Chart deleted successfully."}, status=status.HTTP_200_OK
            )
        except Chart.DoesNotExist:
            return Response(
                {"error": "Chart not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Visualization.DoesNotExist:
            return Response(
                {"error": "Visualization not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RecommendChartView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RecommendVisualizationSerializer(data=request.data)

        if serializer.is_valid():
            file_id = serializer.validated_data.get("file_id")  # Using file_id now
            if not ObjectId.is_valid(file_id):
                return Response(
                    {"error": "Invalid file ID format."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            file = get_object_or_404(File, _id=ObjectId(file_id))  # Fetching by file_id
            filename = file.filename
            chart_name = serializer.validated_data.get("chart_name")
            x_axis = serializer.validated_data.get("x_axis")
            y_axis = serializer.validated_data.get("y_axis")

            image_path = perform_visualize(
                filename=filename,
                chart_name=chart_name,
                x_axis=x_axis,
                y_axis=y_axis,
                folder="visualizations",
            )

            if image_path:
                return Response(image_path, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        "message": "It might be an error with your dataset. Please contact us."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========== NOT BEING USED ================
class ViewTypeDataset(APIView):
    def get(self, request, *args, **kwargs):
        file_id = kwargs.get("file_id")
        # Validate the file_id format
        if not ObjectId.is_valid(file_id):
            return Response(
                {"error": "Invalid file ID format."}, status=status.HTTP_400_BAD_REQUEST
            )
        file = get_object_or_404(File, _id=ObjectId(file_id))
        filename = file.filename
        data_type_dataset = view_type_dataset(filename)

        if data_type_dataset:
            return Response({"data": data_type_dataset}, status=status.HTTP_200_OK)

        return Response(
            {
                "message": "It might be problem with your file please check your file or contact us."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class FindKPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FindKPISerializer(data=request.data)

        if serializer.is_valid():
            file_id = serializer.validated_data.get("file_id")
            try:
                file = get_object_or_404(File, _id=ObjectId(file_id))
            except Exception as e:
                return Response(
                    {"error": f"Invalid ObjectId: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
                return Response(
                    {
                        "message": "It might be a problem with your file. Please check or contact us."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        logger.error(f"Invalid serializer data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
