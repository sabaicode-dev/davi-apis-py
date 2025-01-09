import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import uuid


def connect_to_mysql(host, user, password, database):
    """
    Establishes a connection to the MySQL database using dynamic inputs.
    """
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


def fetch_data_from_mysql(host, user, password, database, table_name):
    """
    Fetches data from the MySQL database dynamically.

    Args:
        host (str): MySQL host.
        user (str): MySQL username.
        password (str): MySQL password.
        database (str): MySQL database name.
        table_name (str): Table name to fetch data from.
    """
    connection = connect_to_mysql(host, user, password, database)
    if not connection:
        return {"error": "Failed to connect to the database"}

    try:
        cursor = connection.cursor(dictionary=True)
        query = f"SELECT * FROM {table_name}"  # Use table_name dynamically
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        return {"error": str(e)}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def save_table_data_to_csv(data, table_name, file_server_path_file):
    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        # Generate a unique filename
        filename = f"{table_name}_{uuid.uuid4().hex}.csv"
        # Full path to save the file
        save_as = os.path.join(file_server_path_file, filename)
        # Save DataFrame to CSV
        df.to_csv(save_as, index=False)
        return filename  # Return the filename if successful
    except Exception as e:
        return {"error": f"Failed to save CSV: {str(e)}"}
