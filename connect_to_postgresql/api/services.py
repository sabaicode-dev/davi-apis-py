import psycopg
from psycopg.errors import OperationalError
import pandas as pd
import uuid
import os


def fetch_data_from_postgresql(dbname, user, password, host, port, tables=None, query=None):
    """
    Fetch data from a PostgreSQL database dynamically using provided credentials.

    - If `tables` is a list, fetches data from each table.
    - If `query` is provided, executes the given query.
    """
    try:
        # Connect to the database
        connection = psycopg.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )

        with connection.cursor() as cursor:
            if tables:  # Fix: Check if 'tables' is provided and is not empty
                results = {}
                for table in tables:
                    sql_query = f"SELECT * FROM {table}"
                    cursor.execute(sql_query)
                    data = cursor.fetchall()
                    column_names = [desc[0] for desc in cursor.description]
                    results[table] = [dict(zip(column_names, row))
                                      for row in data]
                return results

            elif query:  # If 'query' is provided, execute it
                cursor.execute(query)
                data = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                return {"query_result": [dict(zip(column_names, row)) for row in data]}

            else:
                return {"error": "Either 'tables' or 'query' must be provided."}

    except OperationalError as e:
        raise ValueError(f"Database connection error: {e}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()


def save_table_data_to_csv(data, table_name, file_server_path_file):
    """
    Save fetched data to a CSV file.

    :param data: Fetched data as a list of dictionaries
    :param table_name: Name of the table being saved
    :param file_server_path_file: Path to save the CSV files
    :return: Filename of the saved CSV or an error message
    """
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        if df.empty:
            return {"error": "No data available to save to CSV."}

        # Generate a unique filename
        filename = f"{table_name}_{uuid.uuid4().hex}.csv"
        # Full path to save the file
        save_as = os.path.join(file_server_path_file, filename)

        # Ensure the directory exists
        os.makedirs(file_server_path_file, exist_ok=True)

        # Save DataFrame to CSV
        df.to_csv(save_as, index=False)

        return filename  # Return the filename if successful
    except Exception as e:
        return {"error": f"Failed to save CSV: {str(e)}"}
