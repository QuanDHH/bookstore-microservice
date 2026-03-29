from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomerManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class Customer(AbstractBaseUser, PermissionsMixin):
    username     = models.CharField(max_length=150, unique=True)
    email        = models.EmailField(unique=True)
    full_name    = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    address      = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    objects = CustomerManager()

    USERNAME_FIELD  = "username"
    REQUIRED_FIELDS = ["email", "full_name"]

    class Meta:
        db_table = "customers"

    def __str__(self):
        return f"{self.username} ({self.email})"