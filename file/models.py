from django.db import models
import uuid
import os
from uuid import uuid4
from django.utils import timezone

def rename_uploaded_file(instance, filename):
    # Extract the file extension
    ext = filename.split('.')[-1]
    
    # Create a new filename using UUID (you can use any logic here)
    new_filename = "{}.{}".format(uuid4(), ext)
    
    # Return the new filename
    return os.path.join('uploaded_files/', new_filename)

class File(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=100, null=False)
    file = models.CharField(max_length=200, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    size = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_original = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_sample = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'file'
        verbose_name_plural = 'files'
        db_table = "files"
