from djongo import models
from project.models import Project
from django.db import models
from bson import ObjectId
import uuid

class File(models.Model):
    # _id = models.ObjectIdField(primary_key=True, default=ObjectId)
    _id = models.CharField(primary_key=True, max_length=24, default=lambda: str(ObjectId()))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    filename = models.CharField(max_length=100, null=False)
    file = models.CharField(max_length=200, null=True)
    size = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
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
        verbose_name = "db_datasource"
        verbose_name_plural = "files"
        db_table = "files"
        # Optionally disable auto ID generation
        auto_created = False
        managed = True
