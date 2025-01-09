from django.urls import path
from .views import FetchDatabaseDataView

urlpatterns = [
    path('fetch-database-data/', FetchDatabaseDataView.as_view(),
         name='fetch-database-data'),
]
