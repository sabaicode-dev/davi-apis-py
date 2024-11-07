
from django.urls import path, include

from cleansing.api.view import (FileUploadView,FileUploadFindInncurateDataView,
                        ProcessCleaningFile,CleansingWithShellScript,CleansingTest)

urlpatterns =   [

    path("upload/<int:pk>/",FileUploadView.as_view() , name="upload-file-cleansing"),
    path("find-anaccurate-file/",FileUploadFindInncurateDataView.as_view(), name="find-anaccurate-file"),
    path("processing-cleaning-file/",ProcessCleaningFile.as_view(), name="processing-cleleaning"),
    path("overview/<int:created_by>/<str:uuid>/",CleansingWithShellScript.as_view(), name="cleansing-with-shell"),
    path("cleansing-test/",CleansingTest.as_view(), name="cleansing-testing"),

]