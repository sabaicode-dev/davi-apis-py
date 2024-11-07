
from django.urls import path, include
from django.contrib import admin
from django.urls import path,include
from file.api.view import FileUploadView,FileViewImageByName,FindFileByUserView,FileUploadImageView,FileDetailsViews,FileDetailsActionView,DeleteFileView,DownloadFileAPIview,GetAllImagesView,ViewHeaderView,FileViewAllApiView

urlpatterns =   [

    path('file-upload/', FileUploadView.as_view(), name='file-upload'),
    path("user/<str:filename>/",FileViewImageByName.as_view(), name='file-view-image'),
    path("user/",FindFileByUserView.as_view(), name='user-view-file'),
    path("file/<str:uuid>/",DeleteFileView.as_view(), name='user-uuid-file'),
    path("upload/images/", FileUploadImageView.as_view(), name='upload-image'),
    path("file-details/<str:uuid>/", FileDetailsViews.as_view(), name="details-file"),
    path("files-detail-dataset/<str:uuid>/", FileDetailsActionView.as_view(), name="files-detail-file"),
    path("download/<str:filename>/", DownloadFileAPIview.as_view(), name="download-file"),
    path('view/images/', GetAllImagesView.as_view(), name='get-all-images'),    
    path("headers/view/<str:filename>/",ViewHeaderView.as_view(), name='view-header'),
    # get all files updated
    path("files/",FileViewAllApiView.as_view(), name='view-all-file'),
]
# bedbd992f3284aedb7f79bb485688260