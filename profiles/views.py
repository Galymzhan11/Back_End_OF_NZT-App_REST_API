from rest_framework import generics, permissions
from .serializers import UserProfileSerializer, UserProfileEditSerializer, UserRankingSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from django.utils import timezone

User = get_user_model()

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

   
    def get_object(self):
        user = self.request.user
        current_time = timezone.now()

        if user.last_activity_time:
            session_duration = (current_time - user.last_activity_time).total_seconds() / 3600
            user.all_time_activity += session_duration

        user.last_activity_time = current_time
        user.save()

        return user

class UserProfileEditView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileEditSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserRankingView(generics.ListAPIView):
    serializer_class = UserRankingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return User.objects.all().order_by('-score')