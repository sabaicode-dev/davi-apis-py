from django.db import models
from djongo import models as djongo_models

class Metadata(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, editable=False)
    file_id = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255)
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'metadata'
        unique_together = ('file_id', 'project_id')