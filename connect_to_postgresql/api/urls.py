from django.urls import path
from .views import PostgreSQLDataView

urlpatterns = [
    path(
        "datasets/load-postgresql/",
        PostgreSQLDataView.as_view(),
        name="fetch_postgresql_data",
    ),
]
