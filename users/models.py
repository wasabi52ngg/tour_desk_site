from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

from .valodators import validate_email,validate_phone_number

class User(AbstractUser):
	def user_directory_path(self, filename):
		return f"users/{slugify(self.username)}"

	phone = models.CharField(verbose_name='Телефон', null=False, blank=False,
                             validators=[validate_phone_number])
	photo = models.ImageField(verbose_name='Фото', upload_to=user_directory_path, default=None,
                              blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")



