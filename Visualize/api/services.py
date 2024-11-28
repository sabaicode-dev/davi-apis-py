# services.py
from ..models import YourModel  # Adjust this to your model

def get_all_data():
    return YourModel.objects.all()

def get_data_by_id(data_id):
    return YourModel.objects.get(id=data_id)  # Adjust according to your model
