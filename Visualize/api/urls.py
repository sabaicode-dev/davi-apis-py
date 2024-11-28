# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.VisualizeModelListView.as_view(), name='Visualize-list'),  # List endpoint
    path('list/<int:id>/', views.VisualizeModelListView.as_view(), name='Visualize-detail'),  # Detail endpoint
]
