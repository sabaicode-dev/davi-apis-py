from rest_framework import serializers
from bson import ObjectId
from save_visualize.models import Chart, Visualization

class ChartSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)  # Ensure the `id` is included and read-only
    chartType = serializers.CharField(source="chart_type")
    chartImage = serializers.URLField(source="chart_image")

    class Meta:
        model = Chart
        fields = ['id', 'chartType', 'chartImage', 'description', 'selectedColumns', 'created_at']


class VisualizationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    charts = ChartSerializer(many=True, required=False, default=[])

    class Meta:
        model = Visualization
        fields = ['id', 'name', 'charts', 'created_at']

    def create(self, validated_data):
        charts_data = validated_data.pop('charts', [])
        
        # Create the Visualization instance
        visualization = Visualization.objects.create(**validated_data)

        # Create and save related charts with unique IDs
        for chart_data in charts_data:
            chart_data['id'] = str(ObjectId())  # Generate a MongoDB-compatible ObjectId
            Chart.objects.create(visualization=visualization, **chart_data)

        # Return the visualization instance
        return visualization
