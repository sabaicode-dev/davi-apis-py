from django.urls import path
from drf_yasg.views import get_schema_view  # Correct import from drf_yasg.views
from drf_yasg import openapi

from project.api.view import CreateProject, DeleteProject, ListProject, ProjectDetailView, UpdateProject


urlpatterns = [
    # create project endpoint
    path('project/', CreateProject.as_view(), name="create_project"),
    # get all projects
    path('projects/', ListProject.as_view(), name="list_projects"),
    path('project/<str:project_id>/detail/', ProjectDetailView.as_view(), name="project_detail"),
    path('project/<str:project_id>/update/', UpdateProject.as_view(), name="update_project"),
    path('project/<str:project_id>/delete/', DeleteProject.as_view(), name="delete_project"),
]