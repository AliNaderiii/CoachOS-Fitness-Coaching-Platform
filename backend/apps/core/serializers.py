"""Core serializers for Phase 04 Foundation."""

from rest_framework import serializers


class MetaResponseSerializer(serializers.Serializer):
    app_name = serializers.CharField()
    version = serializers.CharField()
    api_version = serializers.CharField()
    locales = serializers.ListField(child=serializers.CharField())
    default_locale = serializers.CharField()
    auth_strategy = serializers.CharField()
    environment = serializers.CharField()
    capabilities = serializers.ListField(child=serializers.CharField())
    timestamp = serializers.DateTimeField()
