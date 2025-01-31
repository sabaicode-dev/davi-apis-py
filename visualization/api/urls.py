from django.urls import path
from visualization.api.views import (
    ChartCreateView,
    ChartDeleteView,
    RecommendChartView,
    ViewTypeDataset,
    FindKPIView,
    VisualizationDetailViewUpdateDelete,
    VisualizationListCreateView,
)

urlpatterns = [
    # RECOMMENDED CHART ENDPOINTS
    path("charts", RecommendChartView.as_view(), name="visualization-view"),
    # VISUALIZATIONS ENDPOINTS
    path(
        "visualizations/",
        VisualizationListCreateView.as_view(),
        name="visualization-list-create",
    ),
    path(
        "visualizations/<str:pk>/",
        VisualizationDetailViewUpdateDelete.as_view(),
        name="visualization-detail",
    ),
    path(
        "visualizations/<str:visualization_id>/charts/",
        ChartCreateView.as_view(),
        name="chart-create",
    ),
    path(
        "visualizations/<str:visualization_id>/charts/<str:chart_id>/",
        ChartDeleteView.as_view(),
        name="chart-delete",
    ),
    # BELOW API ENDPOINTS ARE NOT BEING USED
    path(
        "view-type-dataset/<str:file_id>/",
        ViewTypeDataset.as_view(),
        name="visualization-view-header",
    ),
    path("find-kpi/", FindKPIView.as_view(), name="find-kpi"),
]
