from rest_framework import serializers


class ScrapeDataByUrlSerializer(serializers.Serializer):
    url = serializers.CharField(max_length=200, required=True)


class ConfirmDataSetSerializer(serializers.Serializer):

    confirmed_filename = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
    rejected_filename = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )
