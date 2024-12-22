from django.urls import path

from image_visualize.api.view import serve_image

urlpatterns = [
    # Your other URL patterns...
    path('server/files/<str:filename>/', serve_image, name='serve-image'),
]
