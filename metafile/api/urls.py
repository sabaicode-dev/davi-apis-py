from django.contrib import admin
from django.urls import path,include
from metafile.api.view import DatasetViews, FileHandler



urlpatterns = [
    path('upload/', DatasetViews.as_view(), name='upload'),

]