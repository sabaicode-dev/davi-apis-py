from django.urls import path
from .views import PostgreSQLDataView

urlpatterns = [
    path('fetch-data/', PostgreSQLDataView.as_view(),
         name='fetch_postgresql_data'),
]
