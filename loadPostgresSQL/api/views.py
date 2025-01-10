from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import fetch_data_from_postgresql, save_table_data_to_csv
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")


class PostgreSQLDataView(APIView):
    """
    API View to fetch data dynamically from PostgreSQL and save to CSV.
    """

    def post(self, request):
        # Extract user input from the request body
        dbname = request.data.get("dbname")
        user = request.data.get("user")
        password = request.data.get("password")
        host = request.data.get("host", "localhost")
        port = request.data.get("port", "5432")
        # Accept the 'table' parameter (list)
        tables = request.data.get("table")
        query = request.data.get("query")

        # Validate input
        if not all([dbname, user, password]):
            return Response(
                {"error": "Missing required fields: dbname, user, and password are mandatory."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch data from PostgreSQL
            data = fetch_data_from_postgresql(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port,
                tables=tables,
                query=query
            )

            # Save the data to CSV files
            csv_results = {}
            if tables:
                # Save each table's data
                for table in tables:
                    if table in data:
                        csv_filename = save_table_data_to_csv(
                            data=data[table],
                            table_name=table,
                            file_server_path_file=file_server_path_file
                        )
                        csv_results[table] = csv_filename
                    else:
                        csv_results[table] = {
                            "error": f"No data found for table {table}"}

            elif "query_result" in data:
                # Save the query result if no tables are provided
                csv_filename = save_table_data_to_csv(
                    data=data["query_result"],
                    table_name="query_result",
                    file_server_path_file=file_server_path_file
                )
                csv_results["query_result"] = csv_filename

            return Response({"data": csv_results}, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
