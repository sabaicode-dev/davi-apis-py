from django.urls import path
from file.api.view import (
    FileUploadView, FileDetailsViews, FileDetailsActionView, DeleteFileView,
    DownloadFileAPIview, ProjectFilesView, ViewHeaderView, FileViewAllApiView
)

urlpatterns = [
    # upload files by project
    path('project/file/upload/<str:project_id>/', FileUploadView.as_view(), name='file-upload'),
    # view files by project
    path('projects/<str:project_id>/files/', ProjectFilesView.as_view(), name='project-files'),
    # view file details actually data
    path('project/<str:project_id>/file/<str:uuid>/', FileDetailsViews.as_view(), name="details-file"),
    # view file header data
    path('project/<str:project_id>/headers/view/<str:filename>/', ViewHeaderView.as_view(), name='view-header'),

    path('files-detail-dataset/<str:uuid>/', FileDetailsActionView.as_view(), name="files-detail-file"),

    path('download/<str:filename>/', DownloadFileAPIview.as_view(), name="download-file"),

    path('project/<str:project_id>/file/<str:uuid>/', DeleteFileView.as_view(), name="file-delete"),

    
    path('all/', FileViewAllApiView.as_view(), name='view-all-file'),
]
