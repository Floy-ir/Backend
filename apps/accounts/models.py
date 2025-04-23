from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    uid = models.CharField(max_length=128, unique=True)
    mobile = models.CharField(max_length=32, unique=True)
    created_at = models.PositiveBigIntegerField(default=0)
    modified_at = models.PositiveBigIntegerField(default=0)

    USER_TYPE_ORDINARY = 'ordinary'
    USER_TYPE_ADMIN = 'admin'

    USER_TYPE = (
        (USER_TYPE_ORDINARY, "ordinary"),
        (USER_TYPE_ADMIN, "admin"),
    )
    user_type = models.CharField(max_length=16, choices=USER_TYPE, default=USER_TYPE_ORDINARY)
