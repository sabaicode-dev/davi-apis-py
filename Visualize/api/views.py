# views.py
from rest_framework import generics
from ..models import YourModel  # Adjust this to your model
from .serializers import YourModelSerializer
from .services import get_all_data, get_data_by_id

class VisualizeModelListView(generics.ListCreateAPIView):
    queryset = get_all_data()
    serializer_class = YourModelSerializer

class VisualizeDetailView(generics.RetrieveAPIView):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer

    def get_object(self):
        return get_data_by_id(self.kwargs['id'])
