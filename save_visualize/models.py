from djongo import models

class Visualization(models.Model):
    id = models.ObjectIdField(primary_key=True)  # Use ObjectId as primary key
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Chart(models.Model):
    id = models.ObjectIdField(primary_key=True)  # Use ObjectId as primary key
    visualization = models.ForeignKey(Visualization, on_delete=models.CASCADE, related_name="charts")
    chart_type = models.CharField(max_length=50)
    chart_image = models.URLField()
    description = models.TextField(blank=True, null=True)
    selected_columns = models.JSONField(blank=True, null=True)  # Allow null and blank
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.chart_type} for {self.visualization.name}"