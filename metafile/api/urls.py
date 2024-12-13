from django.urls import path, include
from django.contrib import admin
from metafile.api.view import DatasetViews, FileHandler

urlpatterns = [
    path('upload/', DatasetViews.as_view(), name='upload'),
]