# Generated by Django 5.0.2 on 2024-06-09 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0021_alter_user_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='associate',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]