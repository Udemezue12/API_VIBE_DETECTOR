from django_bolt import serializers
from .models import WebsiteScanResult


class ScanSerializer(serializers.Serializer):
    url :str


class ScanResultSchema(serializers.Serializer):
    class Meta:
        model = WebsiteScanResult
        fields = "__all__"