# file/models.py
from djongo import models as djongo_models  # Use djongo's ObjectIdField
from django.db import models
from bson import ObjectId
import uuid

class File(models.Model):
    _id = djongo_models.ObjectIdField(primary_key=True, default=ObjectId, db_column="id")  # Use MongoDB's default ObjectId
    filename = models.CharField(max_length=100, null=False)
    file = models.CharField(max_length=200, null=True)
    size = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)  # Ensure a unique UUID is always generated
    is_original = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_sample = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'file'
        verbose_name_plural = 'files'
        db_table = "files"
