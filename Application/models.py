from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from .fields import TaskField, DayField, TimeField


class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have an username")
        if not first_name:
            raise ValueError("Users must have an first name")
        if not last_name:
            raise ValueError("Users must have an last name")
        print(self)
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None):
        user = self.create_user(email, username, first_name, last_name, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    telegram_id = models.IntegerField(default=0)
    is_teacher = models.BooleanField(default=0)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'password']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_username(self):
        return self.username

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def is_role_teacher(self):
        return self.is_teacher

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class SchedulingSystem(models.Model):
    holder_name = models.CharField(max_length=100, default='')
    holder = models.CharField(max_length=100, default='')
    task = TaskField(max_length=10)
    day = models.DateField()
    time = TimeField(max_length=10)
    additional_info = models.TextField(blank=True)
