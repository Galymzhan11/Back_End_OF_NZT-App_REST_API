from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/profiles/', include('profiles.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/conf/', include('configurations.urls')),
    path('api/accounts/', include('allauth.urls')),
]