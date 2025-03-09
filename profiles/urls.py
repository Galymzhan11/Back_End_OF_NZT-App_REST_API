from django.urls import path
from .views import UserProfileEditView, UserProfileView, UserRankingView


urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/edit/', UserProfileEditView.as_view(), name='user-profile-edit'),
    path('user-ranking/', UserRankingView.as_view(), name='user-ranking'),
]