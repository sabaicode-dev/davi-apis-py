from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import fetch_data_from_mysql, save_table_data_to_csv
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")


class FetchMySQLDataAPIView(APIView):

    def post(self, request, *args, **kwargs):
        # Get connection details from the request body
        host = request.data.get("host", "localhost")  # Default: localhost
        user = request.data.get("user", "root")  # Default user
        password = request.data.get("password", "")  # Default empty password
        database = request.data.get("database")  # Database name
        table_names = request.data.get("table_names")  # List of table names

        # Validate required parameters
        if not all([user, database, table_names]):
            return Response(
                {"error": "Missing required parameters: user, database, table_names"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(table_names, list):
            return Response(
                {"error": "table_names must be a list of table names."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch data and generate CSV files
        file_map = {}
        success_count = 0
        error_count = 0

        for table_name in table_names:
            # Fetch data for the table
            data = fetch_data_from_mysql(
                host, user, password, database, table_name)
            if "error" in data:
                file_map[table_name] = {"error": data["error"]}
                error_count += 1
                continue

            # Save data to CSV using the utility function
            result = save_table_data_to_csv(
                data, table_name, file_server_path_file)
            if isinstance(result, dict) and "error" in result:
                file_map[table_name] = result  # Capture the error message
                error_count += 1
            else:
                file_map[table_name] = result
                success_count += 1

        # Build the response
        response_status = (
            status.HTTP_207_MULTI_STATUS if error_count > 0 else status.HTTP_200_OK
        )
        response = {
            "status": response_status,
            "success_count": success_count,
            "error_count": error_count,
            "data": file_map,
        }

        return Response(response, status=response_status)
