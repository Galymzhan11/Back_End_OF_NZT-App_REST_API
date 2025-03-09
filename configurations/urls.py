from django.urls import path
from .views import UserNotifySettingView, UserLanguageSettingView

urlpatterns = [
    path('notify/', UserNotifySettingView.as_view(), name='user-notify-settings'),
    path('language/', UserLanguageSettingView.as_view(), name='user-language-settings'),
]