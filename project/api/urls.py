from django.urls import path
from project.api.view import (
    ProjectDetailUpdateDeleteView,
    ProjectListCreateView,
)


urlpatterns = [
    path("projects/", ProjectListCreateView.as_view(), name="project-list-create"),
    path(
        "projects/<str:project_id>/",
        ProjectDetailUpdateDeleteView.as_view(),
        name="project-detail-update-delete",
    ),
]
