from .services import connect_to_database, fetch_table_data, save_data_to_csv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dotenv import load_dotenv
import os
import logging
import pymysql

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")


class FetchMariaDBDataAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract request parameters
        host = request.data.get("host", "localhost")
        user = request.data.get("user", "root")
        password = request.data.get("password", "")
        database = request.data.get("database")
        table_names = request.data.get("table_names")
        query = request.data.get("query")

        # Validate required inputs
        if not all([database, (table_names or query)]):
            return Response(
                {"error": "Missing required parameters: database, and either table_names or query."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if table_names and not isinstance(table_names, list):
            return Response(
                {"error": "table_names must be a list of table names."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Initialize connection and response
        connection = connect_to_database(host, user, password, database)
        if not connection:
            return Response(
                {"error": "Failed to connect to the database."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        file_map = {}
        success_count = 0
        error_count = 0

        try:
            with connection.cursor() as cursor:
                if query:
                    # Execute custom query
                    cursor.execute(query)
                    data = cursor.fetchall()
                    csv_result = save_data_to_csv(
                        data, "custom_query", file_server_path_file)
                    if isinstance(csv_result, dict) and "error" in csv_result:
                        file_map["custom_query"] = csv_result
                        error_count += 1
                    else:
                        file_map["custom_query"] = csv_result
                        success_count += 1
                else:
                    for table_name in table_names:
                        data = fetch_table_data(cursor, table_name)
                        if isinstance(data, dict) and "error" in data:
                            file_map[table_name] = data
                            error_count += 1
                        else:
                            csv_result = save_data_to_csv(
                                data, table_name, file_server_path_file)
                            if isinstance(csv_result, dict) and "error" in csv_result:
                                file_map[table_name] = csv_result
                                error_count += 1
                            else:
                                file_map[table_name] = csv_result
                                success_count += 1
        except Exception as e:
            return Response(
                {"error": f"Failed to process the request: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            connection.close()

        # Build and return the response
        response_status = (
            status.HTTP_207_MULTI_STATUS if error_count > 0 else status.HTTP_200_OK
        )
        response = {
            "success_count": success_count,
            "error_count": error_count,
            "data": file_map,
        }
        return Response(response, status=response_status)
