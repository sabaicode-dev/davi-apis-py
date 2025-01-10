from django.urls import path
from metafile.api.view import DatasetViews, UpdateMetadataDescriptionView

urlpatterns = [
    path('upload/', DatasetViews.as_view(), name='upload'),
    path('update-description/', UpdateMetadataDescriptionView.as_view(), name='update-description'),
]
