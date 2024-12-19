from djongo import models as djongo_models
from project.models import Project
from django.db import models
from bson import ObjectId
import uuid

class File(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="files")
    filename = models.CharField(max_length=100, null=False)
    file = models.CharField(max_length=200, null=True)
    size = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=50, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.CharField(max_length=36, unique=True, editable=False, default=uuid.uuid4)
    is_original = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_sample = models.BooleanField(default=False)

    original_file = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cleansed_files",
    )

    class Meta:
        verbose_name = "file"
        verbose_name_plural = "files"
        db_table = "files"
