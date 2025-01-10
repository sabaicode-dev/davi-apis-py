from django.urls import path
from .views import LoadMongoDataView, ConfirmDataSetView, ViewDataSetByFilenameView

urlpatterns = [
    path('load/mongo_data/',
         LoadMongoDataView.as_view(), name='load-mongo-data'),
    path('project/<str:project_id>/comfirmData/mongo_data/',
         ConfirmDataSetView.as_view(), name='comfirm-mongo-data'),
    path("project/<str:project_id>/load-mongo/view-dataset/<str:filename>/",
         ViewDataSetByFilenameView.as_view(), name="view-dataset-by-filename")
]
