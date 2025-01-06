from django.urls import path
from .views import (
    VisualizationListCreateView,
    VisualizationDetailView,
    ChartCreateView,
)

urlpatterns = [
    path('visualizations/', VisualizationListCreateView.as_view(), name='visualization-list-create'),
    path('visualizations/<str:pk>/', VisualizationDetailView.as_view(), name='visualization-detail'),
    path('visualizations/<str:visualization_id>/charts/', ChartCreateView.as_view(), name='chart-create'),
]