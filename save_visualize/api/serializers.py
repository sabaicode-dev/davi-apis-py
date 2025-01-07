from rest_framework import serializers
from bson import ObjectId
from save_visualize.models import Chart, Visualization

class ChartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)  # Directly use ObjectId

    class Meta:
        model = Chart
        fields = ['id', 'chart_type', 'chart_image', 'description', 'selectedColumns', 'created_at']


class VisualizationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)  # Directly use ObjectId
    charts = ChartSerializer(many=True, required=False)

    class Meta:
        model = Visualization
        fields = ['id', 'name', 'charts', 'created_at']

    def create(self, validated_data):
        charts_data = validated_data.pop('charts', [])
        visualization = Visualization.objects.create(**validated_data)

        for chart_data in charts_data:
            Chart.objects.create(visualization=visualization, **chart_data)

        return visualization
