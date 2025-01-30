from django.urls import path
from file.api.view import (
    ProjectFilesViewUpload,
    FileDetailsViewDelete,
    FileDownloadView,
    FileHeadersView,
)

urlpatterns = [
    # Project files
    path(
        "projects/<str:project_id>/files/",
        ProjectFilesViewUpload.as_view(),
        name="project-files-list-upload",
    ),
    # File operations
    path(
        "projects/<str:project_id>/files/<str:file_id>/",
        FileDetailsViewDelete.as_view(),
        name="file-details-delete",
    ),
    path(
        "projects/<str:project_id>/files/<str:file_id>/download/",
        FileDownloadView.as_view(),
        name="file-download",
    ),
    # File headers
    path(
        "projects/<str:project_id>/files/<str:file_id>/headers/",
        FileHeadersView.as_view(),
        name="file-headers",
    ),
    # File metadata
    # path(
    #     "projects/<str:project_id>/files/<str:file_id>/metadata/",
    #     FileMetadataView.as_view(),
    #     name="file-metadata",
    # ),
]
