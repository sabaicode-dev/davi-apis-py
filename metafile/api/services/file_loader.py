import pandas as pd
import utils.file_utils as file_utils
from rest_framework.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


class FileHandler:
    ALLOWED_EXTENSIONS_FILE = ['.csv', 'json', 'txt', 'xlsx', 'xls']


    def __init__(self, server_path):
        self.server_path = server_path

    @staticmethod
    def detect_separator(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sample = f.read(1024)
                return ';' if sample.count(';') > sample.count(',') else ','
        except Exception as e:
            print(f"Error detecting separator: {e}")
            return ','  # Default to comma if detection fails

    def upload_file_to_server(self, file):
        try:
            file_extension = file_utils.get_file_extension(str(file))
            logger.info(f"Uploaded file extension: {file_extension}")

            if file_extension not in self.ALLOWED_EXTENSIONS_FILE:
                raise ValidationError(f"Unsupported file type: {file_extension}")

            file_name = file_utils.handle_uploaded_file(file)
            logger.info(f"File uploaded successfully: {file_name}")
            return file_name
        except Exception as e:
            logger.error(f"File upload error: {str(e)}", exc_info=True)
            raise


    def load_dataset(self, file_name, chunksize=1000):
        extension = file_utils.get_file_extension(file_name)
        file_path = f"{self.server_path}/{extension}/{file_name}"

        try:
            if extension == 'csv':
                sep = self.detect_separator(file_path)
                reader = pd.read_csv(file_path, chunksize=chunksize, iterator=True, sep=sep, na_values=['', 'NULL'], keep_default_na=False)
            elif extension == 'json':
                reader = pd.read_json(file_path, lines=True, chunksize=chunksize)
            elif extension in ['xls', 'xlsx']:
                reader = pd.read_excel(file_path, chunksize=chunksize, iterator=True)
            else:
                raise ValueError("Unsupported file format")
            
            return reader
        except Exception as e:
            print(f"Error loading dataset: {e}")
            raise e