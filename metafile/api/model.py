from django.db import models

class FileMetadata(models.Model):
    file_id = models.CharField(max_length=36, unique=True)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename