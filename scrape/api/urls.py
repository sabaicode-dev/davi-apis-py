from django.urls import path
from scrape.api.views import ScraperDataByUrlView, ConfirmDataSetView, ViewDataSetByFilenameView

urlpatterns = [
    path("projects/<str:project_id>/scrape/", ScraperDataByUrlView.as_view(), name="auto-scrape"),
    path("projects/<str:project_id>/scrape/confirm-dataset/", ConfirmDataSetView.as_view(), name="confirm-dataset"),
    path("projects/<str:project_id>/scrape/<str:filename>/", ViewDataSetByFilenameView.as_view(), name="view-dataset-by-filename")
]
