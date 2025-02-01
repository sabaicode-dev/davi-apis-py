from django.urls import path
from .views import FetchDatabaseDataView

urlpatterns = [
    path(
        "datasets/load-sql-server/",
        FetchDatabaseDataView.as_view(),
        name="fetch-database-data",
    ),
]
