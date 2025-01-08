from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .services import *
import logging
import uuid
import os
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure, OperationFailure
from .serializers import ConfirmDataSetSerializer
from pagination.pagination import Pagination

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")

logger = logging.getLogger(__name__)


class LoadMongoDataView(APIView):
    def post(self, request):
        uri = request.data.get("uri", "mongodb+srv://default-uri")
        database_name = request.data.get(
            "database", request.data.get("databases", None))
        collection_name = request.data.get("collection", None)

        try:
            if not uri:
                return Response({"error": "MongoDB URI is required."}, status=status.HTTP_400_BAD_REQUEST)

            if not database_name and not collection_name:
                # Get all databases
                databases = get_all_databases(uri)
                if isinstance(databases, str):
                    raise ConnectionFailure(databases)

                if not databases:  # Check if no databases are found
                    return Response(
                        {"error": "No databases found."},
                        status=status.HTTP_404_NOT_FOUND
                    )

                logger.debug(f"Databases fetched: {databases}")
                return Response({
                    "message": "Databases fetched successfully!",
                    "total_databases": len(databases),
                    "data": databases
                }, status=status.HTTP_200_OK)

            elif database_name and not collection_name:
                # Get collections for specified databases
                result = get_multiple_databases(uri, database_name)
                if "error" in result:
                    return Response({"error": result["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                if not result:  # Check if no collections are found
                    return Response(
                        {"error": f"No collections found for database(s): {
                            database_name}"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                logger.debug(f"Databases fetched: {result}")
                return Response({
                    "total_databases": len(result),
                    "data": result
                }, status=status.HTTP_200_OK)

            elif database_name and collection_name:
                # Handle specific collections
                if isinstance(collection_name, str):
                    collection_name = [collection_name]

                result = get_multi_collection(
                    uri, database_name, collection_name)
                if "error" in result:
                    return Response({"error": result["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                if not result:  # Check if no collections are processed
                    return Response(
                        {"error": f"No data found for collections: {collection_name}"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                response_data = {}
                error_count = 0
                for coll_name, data in result.items():
                    if "error" in data:
                        response_data[coll_name] = {"error": data["error"]}
                        error_count += 1
                    else:
                        # Save to CSV if needed
                        filename = f"{coll_name}_{uuid.uuid4().hex}.csv"
                        save_as = file_server_path_file + filename
                        convert_to_csv_file(data["documents"], save_as)
                        response_data[coll_name] = filename

                # Build the response
                response_status = (
                    status.HTTP_207_MULTI_STATUS if error_count > 0 else status.HTTP_200_OK
                )
                return Response({
                    "message": "Collections processed successfully!",
                    "total_collections": len(collection_name),
                    "data": response_data,
                    "errors": error_count
                }, status=response_status)

        except ConnectionFailure:
            logger.error("Failed to connect to MongoDB", exc_info=True)
            return Response({"error": "Failed to connect to MongoDB. Please check the connection URI and try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except OperationFailure as e:
            logger.error(f"MongoDB operation failed: {str(e)}", exc_info=True)
            return Response({"error": f"MongoDB operation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {
                         str(e)}", exc_info=True)
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConfirmDataSetView(APIView):
    def post(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')

        # Ensure the project_id is cast to ObjectId
        try:
            project_id = ObjectId(project_id)
        except Exception:
            return Response(
                {"error": f"Invalid Project ID format: {project_id}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the project exists
        try:
            project = Project.objects.get(_id=project_id)
        except Project.DoesNotExist:
            return Response(
                {"error": f"Project with ID '{project_id}' does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ConfirmDataSetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Save confirmed files
            confirmed_files = serializer.validated_data.get(
                "confirmed_filename", [])
            confirmed = save_file(confirmed_files, str(
                project_id))  # Pass as string

            # Remove rejected files
            rejected_files = serializer.validated_data.get(
                "rejected_filename", [])
            rejected = remove_file(rejected_files)

            return Response({
                "code": 200,
                "confirmed_message": confirmed.get("confirmed_message", {}),
                "rejected_message": rejected,
                "project_id": str(project_id),  # Convert ObjectId to string
                "confirmed_files": confirmed.get("confirmed_files", [])
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An error occurred during file processing: {str(e)}")
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ViewDataSetByFilenameView(APIView):
    pagination_class = Pagination

    def get(self, request, *args, **kwargs):
        # Load dataset based on the filename parameter
        data = load_dataset(filename=kwargs.get('filename'))

        # Check if data is None, meaning file loading might have failed
        if data is None:
            return Response(
                {"detail": "Dataset not found or could not be loaded."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Safely access "data" key, defaulting to an empty list if not present
        records = data.get("data", [])

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(records, request)

        # Build paginated response and attach additional metadata
        paginated_response = paginator.get_paginated_response(result_page).data
        paginated_response["headers"] = list(data.get("header", []))
        paginated_response["file"] = data.get("file", "")
        paginated_response["total"] = data.get("total", None)
        paginated_response["filename"] = kwargs.get('filename')

        return Response(paginated_response)
