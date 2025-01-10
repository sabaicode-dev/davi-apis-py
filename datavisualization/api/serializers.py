# api/serializers.py
from rest_framework import serializers

class ChartRequestSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    x_column = serializers.CharField(max_length=100)
    y_column = serializers.CharField(max_length=100)
    chart_type = serializers.ChoiceField(choices=['line', 'bar', 'scatter'], default='line')
