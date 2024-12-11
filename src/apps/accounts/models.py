from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError('Email must be provided')
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	last_name = models.CharField(_('Last Name'), max_length=150)
	first_name = models.CharField(_('First Name'), max_length=150)
	patronymic = models.CharField(_('Patronymic'), max_length=150, blank=True, null=True)
	phone_number = models.CharField(_('Phone Number'), max_length=20)
	email = models.EmailField(_('Email'), unique=True)

	GENDER_CHOICES = [
		('M', 'Male'),
		('F', 'Female'),
	]
	gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES)
	birth_date = models.DateField(_('Date of Birth'))

	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)

	objects = UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'gender', 'birth_date']

	def __str__(self):
		return f"{self.last_name} {self.first_name} ({self.email})"
