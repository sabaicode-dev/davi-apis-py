# visualization/api/serializers.py

from rest_framework import serializers
from file.models import File
from rest_framework.response import Response
from rest_framework import status



VISUALIZATION = (
    ('line_chart', 'line_chart'),
    ('bar_chart', 'bar_chart'),
    ('area_chart', 'area_chart'),
    ("donut_chart","donut_chart"),
    ('histogram', 'histogram'),
    ('pie_chart', 'pie_chart'),
    ('scatter_plot', 'scatter_plot'),
    ('heatmap', 'heatmap'),
    ('waterfall', 'waterfall'),
    ('column_chart', 'column_chart'),
    ('bubble_chart', 'bubble_chart'),
    ('radar_chart', 'radar_chart'),
)

class VisualizationSerializer(serializers.Serializer):
    chart_name = serializers.ChoiceField(choices=VISUALIZATION)
    x_axis = serializers.CharField(max_length=200)
    y_axis = serializers.CharField(max_length=200)
    file_id = serializers.CharField()  # Change file_uuid to file_id



class FindKPICategorySerializer(serializers.Serializer):

    AGGREGATION_CHOICES = [
        ("first", "first"),
        ("last", "last"),
        ("count_distinct", "count_distinct"),
        ("count","count")
    ]
    
    aggregation = serializers.ChoiceField(choices=AGGREGATION_CHOICES)


class FindKPINumberSerializer(serializers.Serializer): 
    
    AGGREGATION_CHOICES = [
        ("sum", "sum"),
        ("average", "average"),
        ("minimum", "minimum"),
        ("maximum","maximum"),
         ("count_distinct", "count_distinct"),
        ("count", "count"),
        ("standard_deviation","standard_deviation"),
        ("variance","variance"),
        ("median","median"),
    ]
    aggregation = serializers.ChoiceField(choices=AGGREGATION_CHOICES)


class FindKPISerializer(serializers.Serializer):

    VISUALIZATION_CHOICES = [
        ('card', "card")
    ]

    TYPE_FIELD_CHOICES = [
        ("number", "number"),
        ("category", "category"),
    ]

    AGGREGATION_CATEGORY_CHOICES = [
        ("first", "first"),
        ("last", "last"),
        ("count_distinct", "count_distinct"),
        ("count", "count")
    ]
    
    AGGREGATION_NUMBER_CHOICES = [
        ("sum", "sum"),
        ("average", "average"),
        ("minimum", "minimum"),
        ("maximum","maximum"),
        ("count_distinct", "count_distinct"),
        ("count", "count"),
        ("std_deviation","std_deviation"),
        ("variance","variance"),
        ("median","median"),
    ]

    type_field = serializers.ChoiceField(choices=TYPE_FIELD_CHOICES)
    aggregation = serializers.ChoiceField(choices=AGGREGATION_CATEGORY_CHOICES)
    chart_name = serializers.ChoiceField(choices=VISUALIZATION_CHOICES)
    file_id = serializers.CharField()
    fields = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(FindKPISerializer, self).__init__(*args, **kwargs)

        type_field_value = self.initial_data.get('type_field')
        if type_field_value == 'number':
            self.fields['aggregation'].choices = self.AGGREGATION_NUMBER_CHOICES
        elif type_field_value == 'category':
            self.fields['aggregation'].choices = self.AGGREGATION_CATEGORY_CHOICES


    def validate(self, data):
        if data['type_field'] == 'number' and not isinstance(data.get('fields'), list):
            raise serializers.ValidationError("Field must be a list for type 'number'")
        elif data['type_field'] == 'category' and not isinstance(data.get('fields'), list):
            raise serializers.ValidationError("Field must be a string for type 'string'")
        return data



class LineChartSerializer(serializers.Serializer):

    filename = serializers.CharField(max_length=200, required=True)
    x_axis = serializers.CharField(required=True)
    y_axis = serializers.CharField(required=True)

    def validate_y_axis(self, value):
        if not value.isnumeric():
            raise serializers.ValidationError("y_axis should be numeric.")
        return value

class BarChartSerializer(serializers.ModelSerializer):
    
    filename = serializers.CharField(max_length=200, required=True)
    x_axis = serializers.CharField(required=True)
    y_axis = serializers.CharField(required=True)

    def validate_x_axis(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("x_axis should be category.")

        return value

    def validate_y_axis(self, value):
        if not value.isnumeric():
            raise serializers.ValidationError("y_axis should be numeric.")
        return value




class PerformVisualizationSerializer(serializers.Serializer):

    CHART_CHOICES = [
        ('line_chart', LineChartSerializer),
        ('bar_chart', BarChartSerializer),
    ]

    chart_name = serializers.ChoiceField(choices=CHART_CHOICES)

    def to_internal_value(self, data):
        chart_name = data.get('chart_name')
        if chart_name in dict(self.CHART_CHOICES):
            serializer_class = dict(self.CHART_CHOICES)[chart_name]
            serializer = serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            return {'chart_name': chart_name, **serializer.validated_data}
        else:
            raise serializers.ValidationError({"chart_name": "Invalid chart name."})

    def to_representation(self, instance):
        chart_name = instance.get('chart_name')
        if chart_name in dict(self.CHART_CHOICES):
            serializer_class = dict(self.CHART_CHOICES)[chart_name]
            serializer = serializer_class(instance)
            return {'chart_name': chart_name, **serializer.data}
        return {'chart_name': chart_name}