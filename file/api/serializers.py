# file/api/serializers.py

from rest_framework import serializers
from file.models import File
from bson import ObjectId

class FileSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = File
        fields = ['file']


class FileResponeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="_id", read_only=True)

    class Meta:
        model = File
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Convert ObjectId to string for JSON serialization
        if isinstance(representation.get("id"), ObjectId):
            representation["id"] = str(representation["id"])
        return representation


class CreateUserSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="_id", read_only=True)

    class Meta:
        model = File
        fields = '__all__'


class UpdateFileSerializer(serializers.ModelSerializer):  # Ensure this exists
    file = serializers.CharField(max_length=100, required=True)

    class Meta:
        model = File
        fields = ("file",)


class FileQuerySerializer(serializers.Serializer):
    filename = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
