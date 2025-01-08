from bson import ObjectId
from djongo import models

class Notification(models.Model):
    id = models.ObjectIdField(primary_key=True, default=ObjectId, db_column='_id')
    file_name = models.CharField(max_length=255)  # Name of the file or event
    is_read = models.BooleanField(default=False)  # Indicates if the notification is read
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return self.file_name
