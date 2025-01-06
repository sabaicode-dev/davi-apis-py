from django.contrib import admin
from django.urls import path
# from aicomment.api.views import generate_query
from aicomment.api.views import GenerateMongoQueryView
urlpatterns = [
    # path('generate-query/', generate_query, name='generate_query'),
    path('generate-query/', GenerateMongoQueryView.as_view(), name='generate_query'),
]