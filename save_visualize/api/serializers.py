from rest_framework import serializers
from save_visualize.models import Visualization, Chart

class ChartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    chartType = serializers.CharField(source="chart_type")
    chartImage = serializers.URLField(source="chart_image")

    class Meta:
        model = Chart
        fields = ['id', 'chartType', 'chartImage', 'description', 'selected_columns', 'created_at']


class VisualizationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    charts = ChartSerializer(many=True, required=False, default=[])

    class Meta:
        model = Visualization
        fields = ['id', 'name', 'charts', 'created_at']

    def create(self, validated_data):
        charts_data = validated_data.pop('charts', [])
        visualization = Visualization.objects.create(**validated_data)

        # Create and link charts
        for chart_data in charts_data:
            Chart.objects.create(visualization=visualization, **chart_data)

        return visualization

    def update(self, instance, validated_data):
        charts_data = validated_data.pop('charts', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Replace existing charts
        instance.charts.all().delete()
        for chart_data in charts_data:
            Chart.objects.create(visualization=instance, **chart_data)

        return instance
