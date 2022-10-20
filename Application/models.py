from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django import forms


class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None, grade=None):
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
            password=password,
            grade=grade
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, first_name, last_name, password=None, grade=None):
        user = self.create_user(email, username, first_name, last_name, password, grade)
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
    grade = models.CharField(max_length=4, choices=[('9-6', '9-6'), ('9-7', '9-7'), ('10-6', '10-6'), ('10-7', '10-7')])
    telegram_id = models.IntegerField(default=0)
    is_teacher = models.BooleanField(default=0)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'password', 'grade']

    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class SchedulingSystem(models.Model):
    holder = models.CharField(max_length=100, default='')
    holder_name = models.CharField(max_length=100, default='')
    task = models.CharField(max_length=1, choices=[('1', u'task 1'), ('2', u'task 2'), ('3', u'task 3'), ('4', u'task 4'), ('5', u'task 5'), ('6', u'task 6')])
    day = models.DateField()
    time = models.CharField(max_length=1, choices=[('1', u'12:00 - 14:00'), ('2', u'14:00 - 16:00'), ('3', u'16:00 - 18:00')])
    additional_info = models.TextField(blank=True)
    user = models.TextField()
