# Generated by Django 5.1.2 on 2024-10-27 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sitetour', '0004_alter_booking_status_alter_booking_user_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='photo',
        ),
    ]
