# Generated by Django 5.1.2 on 2024-10-27 13:00

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=users.models.User.user_directory_path, verbose_name='Фото'),
        ),
    ]
