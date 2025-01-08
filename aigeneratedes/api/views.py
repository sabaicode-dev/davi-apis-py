from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .service import generate_description

class GenerateDescriptionView(APIView):
    """
    API endpoint to generate a description for visualizing selected columns and chart type.
    """

    def post(self, request):
        # Extract columns and chart type from the request data
        columns = request.data.get("columns", [])  # List of selected columns
        chart_type = request.data.get("chart_type")  # Chart type (e.g., bar, pie)

        # Debugging: Print incoming request data
        print("Received data:", request.data)

        # Validate incoming data
        if not columns:
            return Response(
                {"error": "Columns are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not chart_type:
            return Response(
                {"error": "Chart type is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Call the service to generate a description
            description = generate_description(columns, chart_type)

            # Debugging: Print the description returned by the service
            print("Generated Description:", description)

            # Check if description was returned properly
            if description.startswith("Error"):
                # If there's an error in description generation
                print("Error in description:", description)
                return Response(
                    {"error": description},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Return the successful response
            return Response(
                {"description": description}, status=status.HTTP_200_OK
            )

        except Exception as e:
            # Catch any unexpected errors during description generation
            print(f"Unexpected error: {e}")
            return Response(
                {"error": "An unexpected error occurred during description generation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
