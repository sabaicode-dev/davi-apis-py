from rest_framework import serializers
from file.models import File
from project.models import Project
from bson import ObjectId


class FileResponeSerializer(serializers.ModelSerializer):
    project = serializers.CharField(write_only=True)  # Accept project ID as a string for validation
    project_id = serializers.SerializerMethodField(read_only=True)  # Return project ID as a string in response

    class Meta:
        model = File
        fields = "__all__"

    def validate_project(self, value):
        """Validate the project ID and fetch the corresponding Project instance."""
        if not ObjectId.is_valid(value):
            raise serializers.ValidationError("Invalid Project ID format.")
        try:
            project = Project.objects.get(_id=ObjectId(value))
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project does not exist.")
        return project  # Return the Project instance

    def create(self, validated_data):
        """Override create to handle project as an ObjectId."""
        project = validated_data.pop("project")
        validated_data["project"] = project  # Assign the validated Project instance
        return super().create(validated_data)

    def get_project_id(self, obj):
        """Return the project ID as a string in the response."""
        return str(obj.project._id) if obj.project else None

    def to_representation(self, instance):
        """Ensure MongoDB ObjectId is serialized as a string."""
        representation = super().to_representation(instance)
        if isinstance(representation.get("_id"), ObjectId):
            representation["_id"] = str(representation["_id"])
        return representation


class UpdateFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("file", "filename", "size", "type")


class FileQuerySerializer(serializers.Serializer):
    """Serializer for querying files by parameters."""
    filename = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
