from rest_framework import serializers
from file.models import File

PROCESS_CHOICES = (
    ('delete_missing_row', 'Delete Missing Row'),
    ('delete_duplicate_row', 'Delete Duplicate Row'),
    ('data_type_conversion', 'Data Type Conversion'),
    ('delete_row_outlier', 'Delete Row Outlier'),
    ('impute_by_mean', 'Impute By Mean'),
    ('impute_by_mode', 'Impute By Mode'),
    ('remove_missing_cell', 'Remove Missing Cell'),
)


class CreateFileCleansingSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        exclude = ['_id']


class ProcessFileCleansingSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    process = serializers.MultipleChoiceField(choices=PROCESS_CHOICES)

    def validate_filename(self, value):
        """
        Ensure the filename exists in the database using PyMongo.
        """
        from pymongo import MongoClient
        from django.conf import settings

        client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
        db = client[settings.DATABASES['default']['NAME']]
        file_exists = db.files.find_one({"filename": value})

        if not file_exists:
            raise serializers.ValidationError(f"The file '{value}' does not exist.")
        return value

# Serializer  for metadata
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