from django.db import models
from django.contrib.auth.models import User

class Visualization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visualizations")
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Chart(models.Model):
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name="charts")
    chart_type = models.CharField(max_length=50)
    chart_image = models.URLField()
    description = models.TextField(blank=True, null=True)
    selected_columns = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chart_type} for {self.visualization.name}"
