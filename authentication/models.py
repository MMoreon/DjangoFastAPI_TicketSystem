from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if hasattr(self.model, 'Role'):
            extra_fields.setdefault('role', self.model.Role.ADMIN)
            
        return self.create_user(email, password, **extra_fields)
    
    def __str__(self):
        return f"{self.email} ({self.role})"

class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        USER = 'USR', 'Пользователь'
        ADMIN = 'ADM', 'Администратор'
        SPECIALIST = 'SPC', 'Специалист'
    
    name = models.CharField(max_length=20, verbose_name="Имя пользователя")
    email = models.EmailField(max_length=254, unique=True)
        
    is_active = models.BooleanField(default=True, verbose_name="Флаг активности пользователя")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ в админку")
    
    role = models.CharField(
        max_length=3,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль в системе'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время регистрации")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()


# User.objects = UserManager()