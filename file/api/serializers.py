from rest_framework import serializers
from file.models import File


class FileSerializer(serializers.ModelSerializer):

    file = serializers.FileField()

    class Meta:
        fields = ['file']


class FileResponeSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = '__all__'

class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = '__all__'    

class UpdateFileSerializer(serializers.ModelSerializer):
    
    file = serializers.CharField(max_length=100,required=True)
    class Meta:
        model = File
        fields= ("file",)

class FileQuerySerializer(serializers.Serializer):
    
    filename = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)


class DynamicRecordSerializer(serializers.Serializer):
    # Example of a static field
    # id = serializers.IntegerField()

    # Generic field for dynamic data
    dynamic_data = serializers.SerializerMethodField()

    def get_dynamic_data(self, obj):
        # 'obj' is a dictionary representing a record from your dataset
        # You can transform or return it as is
        return obj