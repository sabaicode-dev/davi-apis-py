from rest_framework import serializers
from metafile.api.models import Metadata
from bson import ObjectId

class ObjectIdField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

class MetadataSerializer(serializers.ModelSerializer):
    _id = ObjectIdField()  # Use the custom field for _id

    class Meta:
        model = Metadata
        fields = '__all__'