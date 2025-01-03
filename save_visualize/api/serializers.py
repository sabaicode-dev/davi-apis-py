from rest_framework import serializers
from save_visualize.models import Visualization, Chart

class ChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chart
        fields = ['id', 'chart_type', 'chart_image', 'description', 'selected_columns', 'created_at']


class VisualizationSerializer(serializers.ModelSerializer):
    charts = ChartSerializer(many=True, read_only=True)

    class Meta:
        model = Visualization
        fields = ['id', 'name', 'charts', 'created_at']
