from django.urls import path
from .views import LoadMongoDataView, ConfirmDataSetView

urlpatterns = [
    path('datasets/load/',
         LoadMongoDataView.as_view(), name='load-mongo-data'),
    path('projects/<str:project_id>/datasets/confirm/',
         ConfirmDataSetView.as_view(), name='comfirm-mongo-data'),
]
