from django.urls import path
from file.api.view import (
    FileUploadView, FileDetailsViews, FileDetailsActionView, DeleteFileView,
    DownloadFileAPIview, ProjectFilesView, ViewHeaderView, FileViewAllApiView
)

urlpatterns = [
    path('project/<str:project_id>/file/upload/', FileUploadView.as_view(), name='file-upload'),
    path('projects/<str:project_id>/files/', ProjectFilesView.as_view(), name='project-files'),
    path('project/<str:project_id>/file/<str:file_id>/details/', FileDetailsViews.as_view(), name="details-file"),
    path('project/<str:project_id>/file/<str:uuid>/delete/', DeleteFileView.as_view(), name="file-delete"),
    path('project/<str:project_id>/headers/view/<str:filename>/', ViewHeaderView.as_view(), name='view-header'),
    path('files-detail-dataset/<str:uuid>/', FileDetailsActionView.as_view(), name="files-detail-file"),
    path('project/<str:project_id>/file/upload/download/<str:filename>/', DownloadFileAPIview.as_view(), name="download-file"),
    path('all/', FileViewAllApiView.as_view(), name='view-all-file'),
]