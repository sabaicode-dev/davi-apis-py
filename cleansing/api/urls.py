from django.urls import path

from cleansing.api.view import CleansingTest, CleansingWithShellScript, FileUploadFindInncurateDataView, ProcessCleaningFile

urlpatterns = [
    path("project/<str:project_id>/file/<str:file_id>/find-anaccurate-file/", FileUploadFindInncurateDataView.as_view(), name="find-anaccurate-file"),
    path("processing-cleaning-file/", ProcessCleaningFile.as_view(), name="processing-cleaning"),
    path("overview/<int:created_by>/<str:uuid>/", CleansingWithShellScript.as_view(), name="cleansing-with-shell"),
    path("cleansing-test/", CleansingTest.as_view(), name="cleansing-testing"),
]
