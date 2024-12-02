# api/views.py
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from rest_framework.response import Response
from rest_framework.views import APIView
from datavisualization.models import DataFile
from django.core.files.base import ContentFile

class GenerateChartView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve query parameters
        file_id = request.query_params.get('file_id')
        x_column = request.query_params.get('x_column')
        y_column = request.query_params.get('y_column')
        chart_type = request.query_params.get('chart_type', 'line')  # Default to line chart

        # Retrieve the file from the database
        try:
            data_file = DataFile.objects.get(id=file_id)
        except DataFile.DoesNotExist:
            return Response({'error': 'File not found'}, status=404)
        
        # Read the data into a pandas DataFrame
        df = pd.read_csv(data_file.file.path)

        # Validate if the requested columns exist in the dataframe
        if x_column not in df.columns or y_column not in df.columns:
            return Response({'error': 'Invalid columns selected'}, status=400)

        # Create the chart
        plt.figure(figsize=(10, 6))
        
        # Handle different chart types
        if chart_type == 'line':
            plt.plot(df[x_column], df[y_column], label=f'{y_column} vs {x_column}')
        elif chart_type == 'bar':
            plt.bar(df[x_column], df[y_column], label=f'{y_column} vs {x_column}')
        elif chart_type == 'scatter':
            plt.scatter(df[x_column], df[y_column], label=f'{y_column} vs {x_column}')
        else:
            return Response({'error': 'Unsupported chart type'}, status=400)
        
        # Set labels and title
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f'{y_column} vs {x_column}')
        plt.legend()

        # Save the plot to a buffer and encode to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        image_data = buffer.getvalue().encode('base64')
        
        return Response({
            'chart': image_data,
            'message': 'Chart generated successfully'
        })
