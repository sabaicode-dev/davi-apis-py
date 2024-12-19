from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('ai_search/', views.ai_search, name='ai_search'),
]
