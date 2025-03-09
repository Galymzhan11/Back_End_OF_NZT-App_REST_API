from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from yookassa import Configuration, Payment
from django.conf import settings
from django.http import JsonResponse
from yookassa.domain.notification import WebhookNotificationFactory
from profiles.models import UserSubjects
from .models import Subject
from django.contrib.auth import get_user_model
import logging

User = get_user_model()


logger = logging.getLogger(__name__)

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subject_id = request.data.get('subject_id')
        description = request.data.get('description', 'Payment for subject')

        try:
            subject = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            return Response({"error": "Subject does not exist"}, status=404)

        amount = subject.sell_price if subject.sell_price else subject.price

        try:
            Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)

            payment = Payment.create({
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"  
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": request.build_absolute_uri('/payment-success/')
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "user_id": request.user.id,
                    "subject_id": subject_id
                }
            })

            return Response({"payment_url": payment.confirmation.confirmation_url})

        except Exception as e:
            return Response({"error": str(e)}, status=500)


class YookassaWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Received webhook request: {request.data}")

        try:
            
            if 'type' not in request.data or 'event' not in request.data:
                logger.error("Missing required fields 'type' or 'event'")
                return JsonResponse({'status': 'error', 'message': 'Parameter "data" should contain "type" and "event" fields'}, status=400)

            
            notification = WebhookNotificationFactory().create(request.data)
            logger.info(f"Parsed notification: {notification}")

            if notification.event == 'payment.succeeded':
                payment = notification.object

                user_id = payment.metadata.get('user_id')
                subject_id = payment.metadata.get('subject_id')

                logger.info(f"Processing payment for user_id={user_id}, subject_id={subject_id}")

                if not user_id or not subject_id:
                    logger.error("Invalid metadata")
                    return JsonResponse({'status': 'error', 'message': 'Invalid metadata'}, status=400)

                user = User.objects.get(id=user_id)
                logger.info(f"User found: {user}")

                UserSubjects.objects.create(
                    user=user,
                    subject_id=subject_id,
                    progress=0,
                    is_bought=True,
                    is_favorite=True
                )
                logger.info("UserSubjects entry created")

            return JsonResponse({'status': 'ok'}, status=200)

        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)