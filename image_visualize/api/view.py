from django.http import FileResponse, Http404
import os

def serve_image(request, filename):
    # Get the path from environment variables or settings
    image_path = os.path.join(os.getenv('FILE_SERVER_PATH_IMAGE', '/default/path/to/images/'), filename)
    
    # Check if the file exists
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type="image/png")  # Adjust content_type as needed
    else:
        raise Http404("Image not found")
