from rest_framework import serializers
from project.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(required=True, max_length=255)
    project_description = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    deleted_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Project
        fields = ['_id', 'project_name', 'project_description', 'created_at', 'updated_at', 'deleted_at']
    