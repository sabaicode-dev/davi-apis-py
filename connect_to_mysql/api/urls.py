from django.urls import path
from .views import FetchMySQLDataAPIView

urlpatterns = [
    path('datasets/load-mysql', FetchMySQLDataAPIView.as_view(),
         name='fetch-mySQl-data'),
]
