from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import bcrypt


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    
    password_hash = models.CharField(max_length=255)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    role = models.ForeignKey(
        'permissions.Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
    
    def set_password(self, raw_password):
        """Хеширует пароль с помощью bcrypt"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, raw_password):
        """Проверяет пароль"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(
            raw_password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    @property
    def password(self):
        """Свойство для совместимости с Django"""
        return self.password_hash
    
    @password.setter
    def password(self, value):
        """Сеттер для совместимости с Django"""
        if value:
            self.set_password(value)
    
    def soft_delete(self):
        """Мягкое удаление пользователя"""
        self.is_active = False
        self.save()
    
    @property
    def is_authenticated(self):
        """Всегда True для не-анонимных пользователей"""
        return True
    
    def __str__(self):
        return self.email


class Session(models.Model):
    """Модель для хранения сессий пользователей"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['user', 'expires_at']),
        ]
    
    def __str__(self):
        return f"Session for {self.user.email}"
