from django.db import models
from file.models import File  # Assuming your File model is in the 'file' app

class Metadata(models.Model):
    metadata_id = models.CharField(max_length=255, unique=True)  # Metadata ID (could be UUID)
    file = models.ForeignKey(File, on_delete=models.CASCADE)  # Link to the uploaded file
    column_order = models.JSONField(default=dict)  # Store column order
    data_types = models.JSONField(default=dict)  # Store data types
    numeric_stats = models.JSONField(default=dict)  # Store numeric stats
    string_stats = models.JSONField(default=dict)  # Store string stats
    datetime_stats = models.JSONField(default=dict)  # Store datetime stats
    unique_values = models.JSONField(default=dict)  # Store unique values for columns
    created_at = models.DateTimeField(auto_now_add=True)  # Store creation time

    def __str__(self):
        return f"Metadata for {self.file.filename}"
