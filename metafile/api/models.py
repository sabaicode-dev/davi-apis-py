from django.db import models
from djongo import models as djongo_models

class Metadata(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, editable=False)  # MongoDB ObjectId
    file_id = models.CharField(max_length=255)  # ID of the file
    project_id = models.CharField(max_length=255)  # ID of the project
    metadata = models.JSONField()  # JSON field for storing metadata
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp on creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto timestamp on update

    class Meta:
        db_table = 'metadata'
        unique_together = ('file_id', 'project_id')  # Ensure unique combination

