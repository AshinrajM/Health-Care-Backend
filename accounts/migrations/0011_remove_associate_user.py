# Generated by Django 5.0.2 on 2024-03-19 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_remove_user_gender'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='associate',
            name='user',
        ),
    ]
