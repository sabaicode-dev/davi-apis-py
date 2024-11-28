from django.db import models

# Create your models here.
class YourModel(models.Model):
    name = models.CharField(max_length=100)  # Example of a string field
    description = models.TextField(blank=True, null=True)  # Optional text field
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for updates

    def __str__(self):
        return self.name  # String representation of the object

    class Meta:
        verbose_name = "Your Model"  # Human-readable singular name
        verbose_name_plural = "Your Models"  # Human-readable plural name
        ordering = ['-created_at']  # Default ordering by creation date (descending)
