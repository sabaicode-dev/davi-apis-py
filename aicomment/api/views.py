from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from aicomment.api.service import QueryService
from aicomment.api.service import MongoDBService

class GenerateMongoQueryView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")
        collection_name = request.data.get("collection_name")

        if not prompt or not collection_name:
            return Response(
                {"error": "Both prompt and collection_name are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify collection exists
            if collection_name not in MongoDBService.get_collection_names():
                return Response(
                    {"error": f"Collection '{collection_name}' not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get collection schema
            schema = MongoDBService.get_collection_schema(collection_name)
            if not schema:
                return Response(
                    {"error": "Unable to generate schema for the collection."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Generate and execute query
            query = QueryService.generate_mongo_query_from_prompt(
                prompt, collection_name, schema
            )
            if 'error' in query:
                return Response({"error": query["error"]}, status=status.HTTP_400_BAD_REQUEST)

            results = QueryService.execute_mongo_query(collection_name, query)
            return Response({
                "query": query,
                "results": results,
                "count": len(results)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )