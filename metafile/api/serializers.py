from rest_framework import serializers
from metafile.api.models import Metadata
from bson import ObjectId

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        """Convert ObjectId to string for representation."""
        if isinstance(value, ObjectId):
            return str(value)
        return value

    def to_internal_value(self, data):
        """Convert string to ObjectId for internal use."""
        if isinstance(data, str) and ObjectId.is_valid(data):
            return ObjectId(data)
        raise serializers.ValidationError("Invalid ObjectId")

class MetadataSerializer(serializers.ModelSerializer):
    _id = ObjectIdField()  # Use the custom field for MongoDB ObjectId

    class Meta:
        model = Metadata
        fields = ['_id', 'file_id', 'project_id', 'metadata', 'description', 'created_at', 'updated_at']

    def validate_description(self, value):
        """Add validation for the description field."""
        if value and len(value) > 500:
            raise serializers.ValidationError("Description is too long (maximum is 500 characters).")
        return value
