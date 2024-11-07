import os
import uuid
from dotenv import load_dotenv
from rest_framework.response import Response
from rest_framework import status

import nbformat
from nbconvert import HTMLExporter


dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)
file_server_path_jupyter = os.getenv("FILE_SERVER_PATH_JUPYTER")

file_server_path_image = os.getenv("FILE_SERVER_PATH_IMAGE")
file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")

file_base_url_jypyter = os.getenv("BASE_UR_JUPYTER")
file_base_url = os.getenv("BASE_URL_FILE")
FILE_TEMPLATE_PATH = os.getenv("FILE_TEMPLATE_PATH")
ALLOWED_EXTENSIONS_IMAGE = ['.jpg', '.png', '.gif',
                            '.bmp', '.tiff', '.tif', '.webp', '.ico', '.svg', '.jpeg',".JPG"]

ALLOWED_EXTENSIONS_FILE = ['.csv', '.json', '.txt', '.xlsx']


def get_file_server_path():
    return file_server_path_image


def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension


def handle_uploaded_file_image(f):

    extension = get_file_extension(f.name)

    filename = str(uuid.uuid4().hex) + extension

    file_size = f.size

    url_image = str(file_base_url)+filename

    with open(file_server_path_image + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return {"filename": filename, "size": str(file_size)+" bytes", "url": url_image}

def remove_file_juypyter(filename):
    path_file = file_server_path_jupyter+filename
    if find_juypyter_by_filename(filename):
        os.remove(path_file)
        return True
    return False


def upload_jupyter(f):

    filename = str(uuid.uuid4().hex) + ".html"
    file_size = f.size


    # process upload
    with open(file_server_path_jupyter + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    file_jupyter = file_server_path_jupyter+filename
    with open(file_jupyter, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # Create an HTML exporter
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'  # You can choose different templates

    # Process the notebook we loaded earlier
    (body, _) = html_exporter.from_notebook_node(notebook)

    # Write to output HTML file
    with open(file_server_path_jupyter+filename, 'w', encoding='utf-8') as f:
        f.write(body)
    return {
        "filename": filename,
        "size": str(file_size)+" bytes",
        "url": file_base_url_jypyter+filename
    }


def handle_uploaded_file(f):

    original_name = str(f)
    original_extension = get_file_extension(original_name)
    name = original_name.replace(original_extension, "")
    filename = str(uuid.uuid4().hex)+get_file_extension(f.name)
    file_size = f.size
    with open(file_server_path_file + filename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return {"filename": filename, "size": str(file_size), "file": original_name, "type": get_file_extension(f.name).replace(".", "")}


def find_juypyter_by_filename(filename):
    files = os.listdir(file_server_path_jupyter)
    for file in files:
        if file == filename:
            return True
    return False

def find_file_by_filename(filename):
    files = os.listdir(file_server_path_file)
    for file in files:
        if file == filename:
            return True
    return False


def find_file_by_name_sourse(filename):
    try:
        file_state = os.stat(file_server_path_file+filename)
        return file_state
    except FileNotFoundError:
        return None