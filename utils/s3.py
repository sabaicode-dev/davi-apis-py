import boto3
import uuid
import os

# Initialize the S3 client
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def give_valid_folder_name(folder_name):
    if not folder_name:
        return True  # Empty folder name is allowed (root of the bucket)

    # Regex to validate folder name
    if folder_name.lower() == "datasets":
        return "datasets"
    elif folder_name.lower() == "visualizations":
        return "visualizations"
    else:
        return "others"


def upload_to_s3(file_buffer, file_extension="png", folder=""):
    """
    Uploads a file buffer to S3 and returns the S3 URL.

    :param file_buffer: The file buffer (e.g., BytesIO object) to upload.
    :param file_extension: The file extension (default is 'png').
    :param folder: The folder (prefix) in the S3 bucket where the file will be stored.
    :return: S3 URL of the uploaded file.
    """
    # Validate the folder name
    dir_name = give_valid_folder_name(folder)

    # Generate a unique filename
    filename = f"{uuid.uuid4().hex}.{file_extension}"

    # Construct the full S3 key (including folder)
    s3_key = f"{dir_name}/{filename}" if folder else filename

    # Upload the file buffer to S3
    s3_client.upload_fileobj(file_buffer, S3_BUCKET_NAME, s3_key)

    # Generate and return the S3 URL
    s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    return s3_url
