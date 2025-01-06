from rest_framework import serializers
from save_visualize.models import Visualization, Chart

class ChartSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    chartType = serializers.CharField(source="chart_type")
    chartImage = serializers.URLField(source="chart_image")

    class Meta:
        model = Chart
        fields = ['id', 'chartType', 'chartImage', 'description', 'selected_columns', 'created_at']

    def get_id(self, obj):
        return str(obj.id)

    def validate_chartType(self, value):
        if not value:
            raise serializers.ValidationError("The 'chartType' field is required.")
        return value
    
    def validate_chartImage(self, value):
        if not value:
            raise serializers.ValidationError("The 'chartImage' field is required.")
        return value

class VisualizationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.CharField(required=True)
    charts = ChartSerializer(many=True, required=False, default=[])

    class Meta:
        model = Visualization
        fields = ['id', 'name', 'charts', 'created_at']

    def get_id(self, obj):
        return str(obj.id)

    def create(self, validated_data):
        charts_data = validated_data.pop('charts', None)  # Use None as default
        print("Validated data for visualization:", validated_data)  # Debugging
        visualization = Visualization.objects.create(**validated_data)

        if charts_data:  # Only process charts if they exist
            for chart_data in charts_data:
                print("Creating chart with data:", chart_data)  # Debugging
                Chart.objects.create(visualization=visualization, **chart_data)

        return visualization

    def update(self, instance, validated_data):
        charts_data = validated_data.pop('charts', [])
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # Clear existing charts and create new ones
        instance.charts.all().delete()
        for chart_data in charts_data:
            chart_serializer = ChartSerializer(data=chart_data)
            chart_serializer.is_valid(raise_exception=True)
            chart_serializer.save(visualization=instance)
        
        return instance

    def validate_name(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("The 'name' field is required and cannot be empty.")
        return value