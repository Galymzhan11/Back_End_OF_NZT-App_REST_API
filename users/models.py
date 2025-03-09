from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils import timezone

class User(AbstractUser, PermissionsMixin):
    id = models.BigAutoField(db_column='Id', primary_key=True)
    email = models.EmailField(db_column='Email', unique=True)
    username = models.CharField(db_column='FirstName', max_length=150, blank=True, null=False)
    lastname = models.CharField(db_column='LastName', max_length=150, blank=True, null=True)
    password = models.CharField(db_column='Password', max_length=128)
    score = models.IntegerField(db_column='Score', default=0)
    role = models.ForeignKey('profiles.Role', db_column='RoleId', on_delete=models.CASCADE, default=0)
    setting = models.ForeignKey('configurations.Setting', db_column='SettingId', on_delete=models.CASCADE, default=1)
    image = models.ForeignKey('profiles.File', db_column='ImageId', on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(db_column='DateCreated', auto_now_add=True)
    date_updated = models.DateTimeField(db_column='DateUpdated', auto_now=True)
    all_time_activity = models.IntegerField(default=0)
    last_activity_time = models.DateTimeField(default=timezone.now)  
   

    is_active = models.BooleanField(db_column='is_active', default=True)
    is_staff = models.BooleanField(db_column='is_staff', default=False)
    is_superuser = models.BooleanField(db_column='is_superuser', default=False)

    first_name = None
    last_name = None
    date_joined = None
    last_login = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_set',
        related_query_name='user',
        db_table='Users_groups', 
        blank=True
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_set',
        related_query_name='user',
        db_table='Users_user_permissions',
        blank=True
    )


    class Meta:
        db_table = 'Users'
        managed = False

    def __str__(self):
        return self.email