from django.urls import path, include
from django.contrib import admin
from metafile.api.view import DatasetViews, MetadataDetailView

urlpatterns = [
    path('upload/', DatasetViews.as_view(), name='upload'),
    path('dataset/', DatasetViews.as_view(), name='dataset_metadata'),
    path('metadata/<str:file_id>/', MetadataDetailView.as_view(), name='metadata_detail'),
]