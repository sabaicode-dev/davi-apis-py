from rest_framework import serializers

class ConfirmDataSetSerializer(serializers.Serializer):

    confirmed_filename = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
    rejected_filename = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
