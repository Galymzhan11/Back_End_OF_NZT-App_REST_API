from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import (
    UserRegistrationView,
    UserVerificationView,
    PasswordResetRequestView,
    PasswordResetCodeVerificationView,
    PasswordResetConfirmView,
    LogoutView,
)

urlpatterns = [
    # кастомные эндпоинты
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('register/verify/', UserVerificationView.as_view(), name='user-verify'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/verify/', PasswordResetCodeVerificationView.as_view(), name='password-reset-verify'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # URL-ы для JWT аутентификации
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]