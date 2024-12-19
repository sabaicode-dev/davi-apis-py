from django.urls import path
from cleansing.api.view import FileUploadFindInaccurateDataView, ProcessCleaningFile
urlpatterns = [
    path(
        "project/<str:project_id>/file/<str:file_identifier>/find-anaccurate-file/",
        FileUploadFindInaccurateDataView.as_view(),
        name="find-anaccurate-file",
    ),
    path(
        "project/<str:project_id>/file/<str:file_identifier>/processing-cleaning-file/",
        ProcessCleaningFile.as_view(),
        name="processing-cleaning",
    )
]