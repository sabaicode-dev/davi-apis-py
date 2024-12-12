from django.urls import path
from metafile.api.view import FileMetadataView, LoadFileView, DatasetViews

urlpatterns = [
    # File upload endpoint
    path('upload/', DatasetViews.as_view(), name='upload'),

    # File metadata endpoint with project and file context
    path('file/<str:file_id>/', FileMetadataView.as_view(), name='file_metadata'),

    # Load file endpoint
    path('file/load/<str:file_id>/', LoadFileView.as_view(), name='load_file'),
]