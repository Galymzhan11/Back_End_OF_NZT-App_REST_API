from rest_framework import generics, permissions
from .serializers import NotifySettingSerializer, LanguageSettingSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserNotifySettingView(generics.UpdateAPIView):
    serializer_class = NotifySettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        setting = user.setting
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        notify = serializer.validated_data['notify']
        setting.notify = notify

        if setting.language == 'ru-RU':  
            new_setting_id = 1 if notify else 2
        elif setting.language == 'en-US':  
            new_setting_id = 3 if notify else 4
        else:
            return Response({"error": "Invalid language"}, status=status.HTTP_400_BAD_REQUEST)

        setting.save()
        user.setting_id = new_setting_id
        user.save()

        return Response({"message": "Notification setting updated", "setting_id": new_setting_id})



class UserLanguageSettingView(generics.UpdateAPIView):
    serializer_class = LanguageSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        setting = user.setting
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        language = serializer.validated_data['language']
        setting.language = language

        # Обновление SettingId
        if language == 'ru-RU':  # Русский
            new_setting_id = 1 if setting.notify else 2
        elif language == 'en-US':  # Английский
            new_setting_id = 3 if setting.notify else 4
        else:
            return Response({"error": "Invalid language"}, status=status.HTTP_400_BAD_REQUEST)

        setting.save()
        user.setting_id = new_setting_id
        user.save()

        return Response({"message": "Language setting updated", "setting_id": new_setting_id})