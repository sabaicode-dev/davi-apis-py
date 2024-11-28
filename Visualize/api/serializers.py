# serializers.py
from rest_framework import serializers
from ..models import YourModel  # Adjust this import to your model

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel  # Replace with your model name
        fields = '__all__'  # Or specify the fields you need: ['field1', 'field2', ...]
