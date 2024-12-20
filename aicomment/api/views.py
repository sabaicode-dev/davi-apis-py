from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .service import generate_mongo_query_from_prompt, execute_mongo_query, get_headers_from_mongo

class GenerateMongoQueryView(APIView):
    """
    API endpoint to generate a MongoDB query based on a prompt and automatically fetch headers, 
    then execute the query and return the results.
    """

    def post(self, request):
        # Extract prompt from the request data
        prompt = request.data.get("prompt")  # The natural language prompt

        # Validate incoming data
        if not prompt:
            return Response(
                {"error": "Prompt is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch headers from the MongoDB collection (you can specify your collection name)
            headers = get_headers_from_mongo("products")  # Replace 'products' with your actual collection name

            if not headers:
                return Response(
                    {"error": "No headers found in the collection."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Generate the MongoDB query using the prompt and headers
            query = generate_mongo_query_from_prompt(prompt, headers)

            # If the query generation was successful, execute it
            if query.startswith("Error"):
                return Response(
                    {"error": query},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Execute the query against MongoDB
            results = execute_mongo_query(query)

            # Return the query results
            return Response(
                {"data": results}, status=status.HTTP_200_OK
            )

        except Exception as e:
            # Handle any unexpected errors
            print(f"Unexpected error: {e}")
            return Response(
                {"error": "An unexpected error occurred during query generation."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
