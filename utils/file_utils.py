import os
import uuid

from utils.load_env import FILE_LOCAL_SERVER_PATH


def get_file_extension(filename):
    return os.path.splitext(filename)[1].lower().replace('.', '')

def handle_uploaded_file(f):
    # Generate unique filename and filepath
    original_name = str(f)
    original_extension = get_file_extension(original_name)  # Returns 'csv', 'json', etc.
    dataset_id = f"{uuid.uuid4().hex}"

    # Create subdirectory based on file type
    destination_dir = os.path.join(FILE_LOCAL_SERVER_PATH, original_extension)
    os.makedirs(destination_dir, exist_ok=True)

    # Define full path for the file
    file_name = f"{dataset_id}.{original_extension}"
    file_path = os.path.join(destination_dir, file_name)
    file_path = os.path.normpath(file_path)

    # Save the file
    try:
        with open(file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    except Exception as e:
        print('error: ', e)
        return {"error": f"Failed to save file: {str(e)}"}

    return file_name
