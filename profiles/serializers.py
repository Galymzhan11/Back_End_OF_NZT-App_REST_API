from rest_framework import serializers
from django.contrib.auth import get_user_model
from storages.backends.s3boto3 import S3Boto3Storage
import io
from django.core.files.base import ContentFile
from users.views import create_initial_image, generate_image_filename, save_image_to_s3
from .models import File, UserSubjects, UserExams


s3_storage = S3Boto3Storage()
User = get_user_model()

def create_default_image_for_user(user):
    default_image_url = 'https://bilimber-profile-images.s3.eu-north-1.amazonaws.com/profile_images/default_profile_image.png'
    file_record = File.objects.filter(file_path=default_image_url).first()
    if not file_record:
        image = create_initial_image(user.username[0].upper())  
        image_buffer = io.BytesIO()
        image.save(image_buffer, format='PNG')
        image_buffer.seek(0)
        file_name = f'profile_images/{user.id}_default.png'
        s3_storage.save(file_name, ContentFile(image_buffer.read()))
        file_url = f'https://{s3_storage.bucket_name}.s3.amazonaws.com/{file_name}'
        file_record = File.objects.create(file_path=file_url)
    return file_record.id

def create_and_save_image(user, image_content=None):
    if image_content:
        file_name = generate_image_filename(user.id, user.username)
        file_url = save_image_to_s3(image_content, file_name)
    else:
        initial = user.username[0].upper()
        image = create_initial_image(initial)
        file_name = generate_image_filename(user.id, image_type="default")
        file_url = save_image_to_s3(image, file_name)

    file_record = File.objects.create(file_path=file_url)
    return file_record.id

class UserProfileEditSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(write_only=True, required=False)
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    remove_image = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'lastname', 'email', 'profile_image', 'old_password', 'new_password', 'remove_image']
        read_only_fields = ['email']

    def validate(self, data):
        if 'old_password' in data or 'new_password' in data:
            if not self.instance.check_password(data.get('old_password', '')):
                raise serializers.ValidationError({'old_password': 'Старый пароль введен неправильно.'})
        return data

    def update(self, instance, validated_data):
        new_username = validated_data.get('username')
        if new_username:
            instance.username = new_username

        new_lastname = validated_data.get('lastname')
        if new_lastname:
            instance.lastname = new_lastname

        if 'new_password' in validated_data and 'old_password' in validated_data:
            instance.set_password(validated_data['new_password'])

        if validated_data.get('remove_image'):
            default_image_id = create_and_save_image(instance)
            instance.image_id = default_image_id
        elif 'profile_image' in validated_data:
            profile_image = validated_data.pop('profile_image')
            image_id = create_and_save_image(instance, image_content=profile_image)
            instance.image_id = image_id

        instance.save()
        return instance

class UserRankingSerializer(serializers.ModelSerializer):

    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'lastname', 'score', 'profile_image_url']

    def get_profile_image_url(self, obj):
        if obj.image:
            try:
                file = File.objects.get(id=obj.image.id)
                return file.file_path 
            except File.DoesNotExist:
                return None
        return None


class UserSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubjects
        fields = ['user_id', 'subject_id', 'progress']

class UserExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExams
        fields = ['user_id','exam_id', 'progress']

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    courses_completed = serializers.SerializerMethodField()
    exams_completed = serializers.SerializerMethodField()
    score = serializers.IntegerField(read_only=True)
    ranking_position = serializers.SerializerMethodField()
    total_time_spent = serializers.FloatField(source='all_time_activity', read_only=True)

    class Meta:
        model = User
        fields = ['username', 'lastname', 'email', 'profile_image', 'courses_completed', 'exams_completed', 'score', 'ranking_position', 'total_time_spent']

    def get_profile_image(self, obj):
        try:
            file_instance = File.objects.get(id=obj.image_id)
            return file_instance.file_path
        except File.DoesNotExist:
            return None

    def get_ranking_position(self, obj):
        ranking = list(User.objects.all().order_by('-score').values_list('id', flat=True))
        return ranking.index(obj.id) + 1

    def get_courses_completed(self, obj):
        return UserSubjects.objects.filter(user_id=obj.id, progress=100).count()

    def get_exams_completed(self, obj):
        return UserExams.objects.filter(user_id=obj.id, progress=100).count()
    
    def get_total_time_spent(self, obj):
        total_time = obj.all_time_activity
        return round(total_time, 1)