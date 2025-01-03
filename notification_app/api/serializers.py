from rest_framework import serializers
from notification_app.models import Notification
from django.contrib.auth.models import User

class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)  # Explicitly handle user field

    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'description', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
