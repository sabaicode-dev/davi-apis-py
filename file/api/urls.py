
from django.urls import path, include
from django.contrib import admin
from django.urls import path,include
from file.api.view import FileUploadView,FileDetailsViews,FileDetailsActionView,DeleteFileView,DownloadFileAPIview,ViewHeaderView,FileViewAllApiView

urlpatterns =   [

    path('file-upload/', FileUploadView.as_view(), name='file-upload'),
    path("file/<str:uuid>/",DeleteFileView.as_view(), name='user-uuid-file'),
    path("file-details/<str:uuid>/", FileDetailsViews.as_view(), name="details-file"),
    path("files-detail-dataset/<str:uuid>/", FileDetailsActionView.as_view(), name="files-detail-file"),
    path("download/<str:filename>/", DownloadFileAPIview.as_view(), name="download-file"),
    path("headers/view/<str:filename>/",ViewHeaderView.as_view(), name='view-header'),
    # get all files updated
    path("files/",FileViewAllApiView.as_view(), name='view-all-file'),
]
# bedbd992f3284aedb7f79bb485688260