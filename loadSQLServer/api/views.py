from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import fetch_data_from_database, save_table_data_to_csv
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")


class FetchDatabaseDataView(APIView):
    """
    View to fetch data from multiple SQL Server database tables or execute a custom SQL query.
    """

    def post(self, request, *args, **kwargs):
        # Retrieve parameters from the request body
        server = request.data.get('server')
        database = request.data.get('database')
        username = request.data.get('username')
        password = request.data.get('password')
        # Optional for fetching tables
        table_names = request.data.get('table_name')
        # Custom SQL query (optional)
        sql_query = request.data.get('sql_query')

        # Validate input parameters
        if not all([server, database, username, password]):
            return Response(
                {"error": "All parameters (server, database, username, password) are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data_response = {}

        try:
            # If `sql_query` is provided, execute the custom query
            if sql_query:
                try:
                    # Fetch data using the service function
                    data = fetch_data_from_database(
                        server, database, username, password, sql_query=sql_query
                    )

                    # Save the query result to a CSV
                    csv_result = save_table_data_to_csv(
                        data, "custom_query", file_server_path_file)

                    if isinstance(csv_result, dict) and "error" in csv_result:
                        return Response(
                            {"error": csv_result["error"]},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                    return Response(
                        {"data": {"custom_query": csv_result}},
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    return Response(
                        {"error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            # If `table_names` is provided, fetch data from the specified tables
            if table_names:
                if not isinstance(table_names, list):
                    return Response(
                        {"error": "The 'table_name' parameter must be a list of table names."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                for table_name in table_names:
                    # Fetch data using the service function
                    data = fetch_data_from_database(
                        server, database, username, password, table_name=table_name
                    )

                    # Save data to CSV
                    csv_result = save_table_data_to_csv(
                        data, table_name, file_server_path_file)

                    if isinstance(csv_result, dict) and "error" in csv_result:
                        # Include error message for the table
                        data_response[table_name] = {
                            "error": csv_result["error"]}
                    else:
                        # Include filename for the table
                        data_response[table_name] = csv_result

                return Response(
                    {"data": data_response},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Either 'table_name' or 'sql_query' must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
