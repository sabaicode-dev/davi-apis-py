from django.http import FileResponse, Http404
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def serve_image(request, filename):
    # Get the image path from the environment variable
    image_base_path = os.getenv('FILE_SERVER_PATH_IMAGE')

    if not image_base_path:
        raise Http404("Image path is not configured in the environment.")

    # Join the base path with the filename
    image_path = os.path.join(image_base_path, filename)

    # Check if the file exists
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type="image/png")  # Adjust content_type if needed
    else:
        raise Http404("Image not found")
