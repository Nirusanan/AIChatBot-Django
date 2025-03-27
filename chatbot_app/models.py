from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class CustomUserManager(BaseUserManager):
    """Manager for CustomUser model"""

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError("The Username field must be set")
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)  # Securely hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom User Model with username-based authentication."""
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username' 
    REQUIRED_FIELDS = ['email'] 

    def __str__(self):
        return self.username


class ChatSession(models.Model):
    chat_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.chat_title


class ChatMessage(models.Model):
    chat = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user_input = models.TextField()
    response = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.time_stamp}"