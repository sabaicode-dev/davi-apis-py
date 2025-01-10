from bson import ObjectId
from djongo import models

class Chart(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId, db_column='_id')
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


class Visualization(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId, db_column='_id')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
