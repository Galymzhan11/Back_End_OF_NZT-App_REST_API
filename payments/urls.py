from django.urls import path
from .views import CreatePaymentView, YookassaWebhookView

urlpatterns = [
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),
    path('yookassa-webhook/', YookassaWebhookView.as_view(), name='yookassa-webhook'),
]