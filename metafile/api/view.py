from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from metafile.api.services.data_cleaning import replace_nan_with_none  # type: ignore
from metafile.api.services.file_loader import FileHandler
from metafile.api.services.metadata_extractor import MetadataExtractor  # type: ignore
from utils.load_env import FILE_LOCAL_SERVER_PATH
        

class DatasetViews(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Ensure the request contains a file
            if 'file' not in request.data:
                return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
            file = request.data['file']

            # Instantiate the FileHandler to handle file operations
            file_handler = FileHandler(server_path=FILE_LOCAL_SERVER_PATH)

            # Upload the file to the local server and get the saved file path
            file_name = file_handler.upload_file_to_server(file=file)

            # Load the dataset (assuming it's a CSV file)
            data = file_handler.load_dataset(file_name)

            # Extract metadata from the data
            extractor = MetadataExtractor(df_iterator=data)
            metadata = extractor.extract()

            # Replace NaN values with None
            cleaned_metadata = replace_nan_with_none(metadata)

            # Return the cleaned metadata as the response
            return Response(cleaned_metadata, status=status.HTTP_201_CREATED)

        except KeyError:
            # Handle case where 'file' is not part of the request
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print('error::: ', e)
            # Handle all other exceptions and return the error message
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
