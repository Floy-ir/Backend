from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string

class User(AbstractUser):
    uid = models.CharField(max_length=128, unique=True)
    mobile = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.PositiveBigIntegerField(default=0)
    modified_at = models.PositiveBigIntegerField(default=0)

    USER_TYPE_ORDINARY = 'ordinary'
    USER_TYPE_ADMIN = 'admin'

    USER_TYPE = (
        (USER_TYPE_ORDINARY, "ordinary"),
        (USER_TYPE_ADMIN, "admin"),
    )
    user_type = models.CharField(max_length=16, choices=USER_TYPE, default=USER_TYPE_ORDINARY)


class OTP(models.Model):
    mobile = models.CharField(max_length=32)
    code = models.CharField(max_length=6)
    uuid = models.CharField(max_length=128, unique=True)
    created_at = models.PositiveBigIntegerField()
    expires_at = models.PositiveBigIntegerField()
    is_used = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    @classmethod
    def generate_code(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    class Meta:
        db_table = 'accounts_otp'


class EitaUser(models.Model):
    uid = models.CharField(max_length=128, unique=True)
    eita_id = models.CharField(max_length=256, unique=True, default="nothing")
    mobile = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.PositiveBigIntegerField(default=0)
    last_login_at = models.PositiveBigIntegerField(default=0)
    initial_message_sent = models.BooleanField(default=False)

    class Meta:
        db_table = 'accounts_eita_user'