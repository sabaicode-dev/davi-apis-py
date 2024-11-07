from django.urls import path, include
from scrape.api.views import (ScraperDataByUrlView,ConfirmDataSetView,ViewDataSetByFilenameView)

urlpatterns = [

    path("url/", ScraperDataByUrlView.as_view(), name="auto-scrape"),
    path("confirm-dataset/",ConfirmDataSetView.as_view(), name="confirm-dataset"),
    path("view-dataset/<str:filename>/",ViewDataSetByFilenameView.as_view(), name="view-dataset-by-filename")
]