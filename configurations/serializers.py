from rest_framework import serializers


class NotifySettingSerializer(serializers.Serializer):
    notify = serializers.BooleanField()

class LanguageSettingSerializer(serializers.Serializer):
    language = serializers.CharField()