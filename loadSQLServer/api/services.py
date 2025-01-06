import pyodbc
import pandas as pd
import uuid
import os


def fetch_data_from_database(server, database, username, password, table_name=None, sql_query=None):
    """
    Fetch data from a SQL Server database table or execute a custom SQL query.

    :param server: Database server
    :param database: Database name
    :param username: Username
    :param password: Password
    :param table_name: Name of the table to fetch data from (optional)
    :param sql_query: Custom SQL query to execute (optional)
    :return: DataFrame containing the query result
    """
    try:
        # Establish connection
        connection = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        print("Database connection successful!")

        # Determine the query
        query = sql_query if sql_query else f"SELECT * FROM {table_name}"

        # Execute the query
        data = pd.read_sql(query, connection)
        return data

    except pyodbc.Error as e:
        print(f"Database connection/query execution failed: {e}")
        raise Exception(f"Database error: {e}")

    finally:
        # Close connection
        if 'connection' in locals():
            connection.close()
            print("Database connection closed.")


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
