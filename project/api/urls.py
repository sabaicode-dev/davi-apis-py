from django.urls import path
from drf_yasg.views import get_schema_view  # Correct import from drf_yasg.views
from drf_yasg import openapi

from project.api.view import CreateProject, DeleteProject, ListProject, ProjectDetailView, UpdateProject

# Generate Swagger Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Project API",
        default_version='v1',
        description="API documentation for the Project app",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),  # Swagger UI for API docs
    # create project endpoint
    path('project/', CreateProject.as_view(), name="create_project"),
    # get all projects
    path('projects/', ListProject.as_view(), name="list_projects"),
    path('project/<str:project_id>/', ProjectDetailView.as_view(), name="project_detail"),
    path('project/<str:project_id>/update/', UpdateProject.as_view(), name="update_project"),
    path('project/<str:project_id>/delete/', DeleteProject.as_view(), name="delete_project"),
]