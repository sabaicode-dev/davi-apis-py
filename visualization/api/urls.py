# visualization/api/urls.py
from django.urls import path
from visualization.api.views import VisualizationApiView,ViewTypeDataset,FindKPIView

urlpatterns = [
    path("", VisualizationApiView.as_view(), name="visualization-view"),
    path("view-type-dataset/<str:uuid_file>/", ViewTypeDataset.as_view(), name="visualization-view-header"),
    path("find-kpi/",FindKPIView.as_view(), name="find-kpi")
]