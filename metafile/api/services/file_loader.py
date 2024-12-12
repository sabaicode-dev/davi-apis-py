# import os
# import pandas as pd
# from django.conf import settings
# from rest_framework.exceptions import ValidationError
# from metafile.api.model import FileMetadata

# class FileLoader:
#     ALLOWED_EXTENSIONS_FILE = ['csv', 'json', 'txt', 'xlsx', 'xls']

#     def __init__(self, server_path):
#         self.server_path = server_path

#     @staticmethod
#     def detect_separator(file_path):
#         try:
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 sample = f.read(1024)
#                 return ';' if sample.count(';') > sample.count(',') else ','
#         except Exception as e:
#             print(f"Error detecting separator: {e}")
#             return ','  # Default to comma if detection fails

#     def upload_file_to_server(self, file):
#         file_extension = self.get_file_extension(str(file))
#         if file_extension not in self.ALLOWED_EXTENSIONS_FILE:
#             raise ValidationError(f"Invalid file type. Allowed types are: {', '.join(self.ALLOWED_EXTENSIONS_FILE)}")

#         file_name = file.name
#         file_path = os.path.join(self.server_path, file_name)

#         # Save file to server
#         with open(file_path, 'wb') as f:
#             for chunk in file.chunks():
#                 f.write(chunk)

#         return file_name

#     @staticmethod
#     def get_file_extension(file_path):
#         return os.path.splitext(file_path)[-1].lower()

#     def load_dataset(self, file_name):
#         file_path = os.path.join(self.server_path, file_name)

#         if not os.path.exists(file_path):
#             raise ValidationError(f"File {file_name} not found on server.")

#         # Load dataset (assuming CSV for simplicity)
#         separator = self.detect_separator(file_path)
#         return pd.read_csv(file_path, sep=separator)
#     def load_file_from_server(file_id):
#         # Fetch metadata using file_id
#         file_metadata = FileMetadata.objects.filter(file_id=file_id).first()
#         if not file_metadata:
#             raise ValidationError("File metadata not found.")

#         # Get file extension and generate the file path
#         file_extension = file_metadata.filename.split('.')[-1]
#         file_path = os.path.join(settings.MEDIA_ROOT, 'files', file_extension, file_metadata.filename)

#         if not os.path.exists(file_path):
#             raise ValidationError("File not found.")

#         return file_path



import os
import pandas as pd
from django.conf import settings
from rest_framework.exceptions import ValidationError
from metafile.api.model import FileMetadata

class FileLoader:
    ALLOWED_EXTENSIONS_FILE = ['csv', 'json', 'txt', 'xlsx', 'xls']

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
        file_extension = self.get_file_extension(str(file))
        if file_extension not in self.ALLOWED_EXTENSIONS_FILE:
            raise ValidationError(f"Invalid file type. Allowed types are: {', '.join(self.ALLOWED_EXTENSIONS_FILE)}")

        file_name = file.name
        file_path = os.path.join(self.server_path, file_name)

        # Save file to server
        with open(file_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        return file_name

    @staticmethod
    def get_file_extension(file_path):
        return os.path.splitext(file_path)[-1].lower()

    def load_dataset(self, file_name):
        file_path = os.path.join(self.server_path, file_name)

        if not os.path.exists(file_path):
            raise ValidationError(f"File {file_name} not found on server.")

        # Load dataset (assuming CSV for simplicity)
        separator = self.detect_separator(file_path)
        return pd.read_csv(file_path, sep=separator)

# Moved load_file_from_server function outside of the FileLoader class
# def load_file_from_server(file_id):
#     # Fetch metadata using file_id
#     file_metadata = FileMetadata.objects.filter(file_id=file_id).first()
#     if not file_metadata:
#         raise ValidationError("File metadata not found.")

#     # Get file extension and generate the file path
#     file_extension = file_metadata.filename.split('.')[-1]
#     file_path = os.path.join(settings.MEDIA_ROOT, 'files', file_extension, file_metadata.filename)

#     if not os.path.exists(file_path):
#         raise ValidationError("File not found.")

#     return file_path
import logging
logger = logging.getLogger(__name__)
def load_file_from_server(file_id):
    logger.info(f"Looking for file with file_id: {file_id}")
    file_metadata = FileMetadata.objects.filter(file_id=file_id).first()
    if not file_metadata:
        logger.error(f"File metadata not found for file_id: {file_id}")
        raise ValidationError("File metadata not found.")