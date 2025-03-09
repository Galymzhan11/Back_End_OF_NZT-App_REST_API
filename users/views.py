from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from django.core.cache import cache
from django.conf import settings
from .models import User
from .serializers import PasswordResetRequestSerializer, validate_password, LogoutSerializer
from PIL import Image, ImageDraw, ImageFont
import io
from profiles.models import File
from datetime import datetime
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.uploadedfile import InMemoryUploadedFile


s3_storage = S3Boto3Storage()


def create_initial_image(initial, background_color="#a3e635", text_color=(0, 0, 0)):
    img_size = (200, 200)
    image = Image.new('RGB', img_size, color=background_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", 100)
    
    text_bbox = draw.textbbox((0, 0), initial, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_position = ((img_size[0] - text_width) // 2, (img_size[1] - text_height) // 2)
    
    draw.text(text_position, initial, fill=text_color, font=font)
    
    return image

def generate_image_filename(user_id, image_type="profile", suffix="png"):
    return f'profile_images/{user_id}_{image_type}_image.{suffix}'

def save_image_to_s3(image, filename):
    
    if s3_storage.exists(filename):
        s3_storage.delete(filename)

    if isinstance(image, InMemoryUploadedFile):
        
        s3_storage.save(filename, image)
    else:
        
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        s3_storage.save(filename, ContentFile(image_buffer.read()))

    return f'https://{s3_storage.bucket_name}.s3.amazonaws.com/{filename}'

def create_and_save_image(user, i, image_content=None):
    if image_content:
        file_name = generate_image_filename(i, user)
        file_url = save_image_to_s3(image_content, file_name)
    else:
        initial = user[0].upper()
        image = create_initial_image(initial)
        file_name = generate_image_filename(i, image_type="default")
        file_url = save_image_to_s3(image, file_name)

    file_record = File.objects.create(file_path=file_url)
    return file_record.id


def send_verification_email(email, code, subject, message):
    send_mail(
        subject,
        message.format(code=code),
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )


class UserRegistrationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    class UserRegistrationSerializer(serializers.Serializer):
        email = serializers.EmailField()
        FirstName = serializers.CharField(max_length=150)
        password = serializers.CharField(write_only=True)
        password_confirm = serializers.CharField(write_only=True)

        def validate(self, data):
            validate_password(data['password'], data['password_confirm'])
            if User.objects.filter(email=data['email']).exists():
                raise serializers.ValidationError("A user with that email already exists.")
            return data

    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.session['registration_data'] = serializer.validated_data

        email = serializer.validated_data['email']
        verification_code = get_random_string(length=4, allowed_chars='0123456789')

        cache.set(f'registration_code_{email}', verification_code, 300)

        send_verification_email(
            email,
            verification_code,
            'Email Verification Code',
            'Your verification code is {code}'
        )

        request.session['registration_data'] = serializer.validated_data

        return Response({"message": "Verification code sent to your email."}, status=200)


class UserVerificationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    class UserVerificationSerializer(serializers.Serializer):
        verification_code = serializers.CharField(max_length=4)

    serializer_class = UserVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification_code = serializer.validated_data['verification_code']
        email = request.session.get('registration_data', {}).get('email')

        if not email:
            return Response({"error": "Email not found in session. Please restart the registration process."}, status=400)

        cached_code = cache.get(f'registration_code_{email}')
        if cached_code is None or cached_code != verification_code:
            return Response({"error": "Invalid or expired verification code."}, status=400)

        user_data = request.session.get('registration_data')
        if not user_data:
            return Response({"error": "Registration data not found. Please restart the registration process."}, status=400)
        
        u = user_data['FirstName']
        i = user_data.get('Id')

        image_id = create_and_save_image(u, i, image_content=None)
        
        user = User.objects.create_user(
            email=user_data['email'],
            username=user_data['FirstName'],
            lastname=user_data.get('LastName', ''),
            password=user_data['password'],
            role_id=user_data.get('RoleId', 0),
            setting_id=user_data.get('SettingId', 1),
            image_id=image_id,  
            score=0,
            date_created=datetime.now(),
            date_updated=datetime.now(),
        )


        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        request.session.pop('registration_data', None)
        cache.delete(f'registration_code_{email}')

        return Response({
            "message": "Registration completed successfully.",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, status=201)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        reset_code = get_random_string(length=4, allowed_chars='0123456789')

        cache.set(f'password_reset_code_{email}', reset_code, 300)

        send_verification_email(
            email,
            reset_code,
            'Password Reset Code',
            'Your password reset code is {code}'
        )

        return Response({"message": "Password reset code sent."}, status=200)


class PasswordResetCodeVerificationView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    class PasswordResetCodeVerificationSerializer(serializers.Serializer):
        reset_code = serializers.CharField(max_length=4)

    serializer_class = PasswordResetCodeVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_code = serializer.validated_data['reset_code']
        email = request.session.get('reset_email')

        if not email:
            return Response({"error": "Email not found in session. Please restart the password reset process."}, status=400)

        cached_code = cache.get(f'password_reset_code_{email}')
        if cached_code is None or cached_code != reset_code:
            return Response({"error": "Invalid or expired reset code."}, status=400)

        request.session['reset_email'] = email

        return Response({"message": "Code verified. Proceed to reset your password."}, status=200)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    class PasswordResetConfirmSerializer(serializers.Serializer):
        new_password = serializers.CharField(write_only=True)
        new_password_confirm = serializers.CharField(write_only=True)

        def validate(self, data):
            validate_password(data['new_password'], data['new_password_confirm'])
            return data

    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required."}, status=400)

        user = User.objects.get(email=email)
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        cache.delete(f'password_reset_code_{email}')

        return Response({"message": "Password successfully changed."}, status=200)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)


        refresh_token = serializer.validated_data["refresh_token"]
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)