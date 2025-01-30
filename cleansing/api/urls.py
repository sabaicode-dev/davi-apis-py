from django.urls import path
from cleansing.api.view import FileAccuracySummaryView, FileAccuracyDetailView, ProcessCleaningFile
from metafile.api.view import MetadataDetailView

urlpatterns = [
     # 1) Summary of data issues (counts only)
    path(
        "projects/<str:project_id>/files/<str:file_identifier>/accuracy/summary/",
        FileAccuracySummaryView.as_view(),
        name="file-accuracy-summary",
    ),
    # 2) Detailed data issues (missing rows, duplicates, outliers) with pagination
    path(
        "projects/<str:project_id>/files/<str:file_identifier>/accuracy/detail/",
        FileAccuracyDetailView.as_view(),
        name="file-accuracy-detail",
    ),
    path(
        "project/<str:project_id>/file/<str:file_identifier>/processing-cleaning-file/",
        ProcessCleaningFile.as_view(),
        name="processing-cleaning",
    ),
    path(
        "metadata/<str:metadata_id>/",
        MetadataDetailView.as_view(),
        name="processing-cleaning",
    ),
]
