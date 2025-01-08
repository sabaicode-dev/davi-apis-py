from django.urls import path
from .views import (
    VisualizationListCreateView,
    VisualizationDetailView,
    ChartCreateView,
    VisualizationDeleteView,
    ChartDeleteView,  # New view for deleting individual charts
)

urlpatterns = [
    # Visualization endpoints
    path('visualizations/', VisualizationListCreateView.as_view(), name='visualization-list-create'),
    path('visualizations/<str:pk>/', VisualizationDetailView.as_view(), name='visualization-detail'),
    path('visualizations/<str:pk>/delete/', VisualizationDeleteView.as_view(), name='visualization-delete'),

    # Chart endpoints
    path('visualizations/<str:visualization_id>/charts/', ChartCreateView.as_view(), name='chart-create'),
    path('visualizations/<str:visualization_id>/charts/<str:chart_id>/delete/', ChartDeleteView.as_view(), name='chart-delete'),
]
