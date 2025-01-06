from django.urls import path
from .views import FetchMariaDBDataAPIView

urlpatterns = [
    path('load/mariadb_data/', FetchMariaDBDataAPIView.as_view(),
         name='fetch-mariadb-data'),
]
