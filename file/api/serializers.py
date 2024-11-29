from rest_framework import serializers
from file.models import File
from project.models import Project
from bson import ObjectId

class FileResponeSerializer(serializers.ModelSerializer):
    project = serializers.CharField(write_only=True)
    project_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = File
        # Explicitly list fields, excluding 'id'
        fields = [
            '_id', 
            'project', 
            'project_id', 
            'filename', 
            'file', 
            'size', 
            'type', 
            'created_at', 
            'uuid', 
            'is_original', 
            'is_deleted', 
            'is_sample', 
            'original_file'
        ]
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Convert _id to string if it's not already
        representation['_id'] = str(instance._id)
        
        # Ensure project_id is a string
        if hasattr(instance, 'project') and instance.project:
            representation['project_id'] = str(instance.project._id)
        
        return representation

    def validate_project(self, value):
        if not ObjectId.is_valid(value):
            raise serializers.ValidationError("Invalid Project ID format.")
        try:
            project = Project.objects.get(_id=ObjectId(value))
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project does not exist.")
        return project

    def create(self, validated_data):
        project = validated_data.pop("project")
        validated_data["project"] = project
        return super().create(validated_data)

    def get_project_id(self, obj):
        return str(obj.project._id) if obj.project else None    

class UpdateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("file", "filename", "size", "type")


class FileQuerySerializer(serializers.Serializer):
    """Serializer for querying files by parameters."""
    filename = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
