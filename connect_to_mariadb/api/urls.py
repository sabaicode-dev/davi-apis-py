from django.urls import path
from .views import FetchMariaDBDataAPIView

urlpatterns = [
    path('datasets/load-mariadb/', FetchMariaDBDataAPIView.as_view(),
         name='fetch-mariadb-data'),
]
