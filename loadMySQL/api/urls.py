from django.urls import path
from .views import FetchMySQLDataAPIView

urlpatterns = [
    path('load/mySQl_data/', FetchMySQLDataAPIView.as_view(),
         name='fetch-mySQl-data'),
]
