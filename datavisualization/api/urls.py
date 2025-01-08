# api/urls.py
from django.urls import path
from datavisualization.api.views import GenerateChartView

urlpatterns = [
    path('generate_chart/', GenerateChartView.as_view(), name='generate_chart'),
]
