from mysql.connector import Error
import pandas as pd
import os
import uuid

from psycopg import logger
import pymysql


def connect_to_database(host, user, password, database):
    """Establishes a connection to the database."""
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Error as e:
        logger.error(f"Error while connecting to MariaDB: {e}")
        return None


def fetch_table_data(cursor, table_name):
    """Fetches data from a specific table."""
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        return data
    except Exception as e:
        return {"error": str(e)}


def save_data_to_csv(data, table_name, save_path):
    """Saves data to a CSV file."""
    try:
        df = pd.DataFrame(data)
        filename = f"{table_name}_{uuid.uuid4().hex}.csv"
        full_path = os.path.join(save_path, filename)
        df.to_csv(full_path, index=False)
        return filename  # Return only the filename
    except Exception as e:
        return {"error": f"Failed to save CSV: {str(e)}"}
