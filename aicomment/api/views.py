# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .service import QueryService, MongoDBService
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os

# class GenerateMongoQueryView(APIView):
#     def post(self, request):
#         prompt = request.data.get("prompt")

#         # Hardcode the collection name
#         collection_name = "projects"  # Replace with your desired collection name

#         if not prompt:
#             return Response(
#                 {"error": "The 'prompt' field is required."}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # Verify collection exists
#             if collection_name not in MongoDBService.get_collection_names():
#                 return Response(
#                     {"error": f"Collection '{collection_name}' not found."}, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             # Get collection schema
#             schema = MongoDBService.get_collection_schema(collection_name)
#             if not schema:
#                 return Response(
#                     {"error": "Unable to generate schema for the collection."}, 
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )

#             # Generate and execute query
#             query = QueryService.generate_mongo_query_from_prompt(
#                 prompt, collection_name, schema
#             )
#             if 'error' in query:
#                 return Response({"error": query["error"]}, status=status.HTTP_400_BAD_REQUEST)

#             # Validate the query before execution
#             if not isinstance(query, dict):
#                 return Response(
#                     {"error": "Invalid query format. Expected a dictionary."}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             results = QueryService.execute_mongo_query(collection_name, query)
#             return Response({
#                 "query": query,
#                 "results": results,
#                 "count": len(results)
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"An unexpected error occurred: {e}")
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


class GenerateMongoQueryView(APIView):
    def post(self, request):
        prompt = request.data.get("prompt")

        # Hardcode the collection name
        collection_name = "projects"  # Replace with your desired collection name

        if not prompt:
            return Response(
                {"error": "The 'prompt' field is required."}, 
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

            # Generate the MongoDB query
            query = QueryService.generate_mongo_query_from_prompt(
                prompt, collection_name, schema
            )
            if 'error' in query:
                return Response({"error": query["error"]}, status=status.HTTP_400_BAD_REQUEST)

            # Return only the query
            return Response({
                "query": query
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# class GenerateMongoQueryView(APIView):
#     def post(self, request):
#         prompt = request.data.get("prompt")

#         # Derive collection name from an environment variable
#         collection_name = os.getenv("DEFAULT_COLLECTION_NAME", "projects")  # Fallback to 'projects'

#         if not prompt:
#             return Response(
#                 {"error": "The 'prompt' field is required."}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             # Verify collection exists
#             if collection_name not in MongoDBService.get_collection_names():
#                 return Response(
#                     {"error": f"Collection '{collection_name}' not found."}, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             # Get collection schema
#             schema = MongoDBService.get_collection_schema(collection_name)
#             if not schema:
#                 return Response(
#                     {"error": "Unable to generate schema for the collection."}, 
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )

#             # Generate and execute query
#             query = QueryService.generate_mongo_query_from_prompt(
#                 prompt, collection_name, schema
#             )
#             if 'error' in query:
#                 return Response({"error": query["error"]}, status=status.HTTP_400_BAD_REQUEST)

#             results = QueryService.execute_mongo_query(collection_name, query)
#             return Response({
#                 "query": query,
#                 "results": results,
#                 "count": len(results)
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             logger.error(f"An unexpected error occurred: {e}")
#             return Response(
#                 {"error": f"An unexpected error occurred: {str(e)}"}, 
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )