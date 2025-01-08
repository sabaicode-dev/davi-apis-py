from django.urls import path
from scrape.api.views import ScraperDataByUrlView, ConfirmDataSetView, ViewDataSetByFilenameView

urlpatterns = [
    path("project/<str:project_id>/scrape/url/", ScraperDataByUrlView.as_view(), name="auto-scrape"),
    path("project/<str:project_id>/scrape/confirm-dataset/", ConfirmDataSetView.as_view(), name="confirm-dataset"),
    path("project/<str:project_id>/scrape/view-dataset/<str:filename>/", ViewDataSetByFilenameView.as_view(), name="view-dataset-by-filename")
]
