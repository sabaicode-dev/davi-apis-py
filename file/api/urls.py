from django.urls import path
from file.api.view import (
    FileUploadView, FileDetailsViews, FileDetailsActionView, DeleteFileView,
    DownloadFileAPIview, ProjectFilesView, ViewHeaderView, FileViewAllApiView
)

urlpatterns = [
    path('file/upload/<str:project_id>/', FileUploadView.as_view(), name='file-upload'),
    path('projects/<str:project_id>/files/', ProjectFilesView.as_view(), name='project-files'),
    path('details/<str:uuid>/', FileDetailsViews.as_view(), name="details-file"),
    path('files-detail-dataset/<str:uuid>/', FileDetailsActionView.as_view(), name="files-detail-file"),
    path('download/<str:filename>/', DownloadFileAPIview.as_view(), name="download-file"),
    path('headers/view/<str:filename>/', ViewHeaderView.as_view(), name='view-header'),
    path('all/', FileViewAllApiView.as_view(), name='view-all-file'),
]
