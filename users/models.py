
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone, name, password=None):
        if not phone:
            raise ValueError('Phone number is required')
        user = self.model(phone=phone, name=name)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password):
        user = self.model(phone=phone, name=name)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone


class OTP(models.Model):
    phone = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    provider_verification_id = models.CharField(max_length=255, null=True, blank=True)
    provider_transaction_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.phone} - {self.otp_code}"