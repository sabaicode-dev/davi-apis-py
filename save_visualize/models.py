from bson import ObjectId
from djongo import models

class Chart(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)  # Auto-generate ObjectId
    visualization = models.ForeignKey(
        'Visualization',
        on_delete=models.CASCADE,
        related_name="charts"
    )
    chart_type = models.CharField(max_length=50)
    chart_image = models.URLField()
    description = models.TextField(blank=True, null=True)
    selectedColumns = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chart_type} for {self.visualization.name}"


class Visualization(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId)  # Auto-generate ObjectId
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
