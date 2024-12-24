from django.http import FileResponse, Http404
import os

def serve_image(request, filename):
    # Set the path where images are stored
    image_path = os.path.join('D://just-test//davi-apis-py//server//images//', filename)
    
    # Check if the file exists
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type="image/png")  # You can change the content_type based on your image format
    else:
        raise Http404("Image not found")
