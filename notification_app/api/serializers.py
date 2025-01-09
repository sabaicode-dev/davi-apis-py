from rest_framework import serializers
from notification_app.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='pk', read_only=True)  # Ensure id is serialized as a string

    class Meta:
        model = Notification
        fields = ['id', 'file_name', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
