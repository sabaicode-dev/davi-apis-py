from django.http import FileResponse, Http404
from django.conf import settings
import os

def serve_image(request, filename):
    """
    Serve an image file from the server.
    
    :param request: Django HTTP request object
    :param filename: Name of the image file to serve
    :return: FileResponse with the image file or Http404 if not found
    """
    # Dynamically resolve the image directory path from settings or environment
    image_dir = os.getenv('FILE_SERVER_PATH_IMAGE', settings.MEDIA_ROOT)
    image_path = os.path.join(image_dir, filename)
    
    # Check if the file exists and serve it
    if os.path.exists(image_path) and os.path.isfile(image_path):
        try:
            return FileResponse(open(image_path, 'rb'), content_type="image/png")  # Adjust content_type as needed
        except Exception as e:
            raise Http404(f"Error opening file: {e}")
    else:
        raise Http404("Image not found")
