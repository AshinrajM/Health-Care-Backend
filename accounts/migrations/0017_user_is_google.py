# Generated by Django 5.0.2 on 2024-04-05 04:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_associate_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_google',
            field=models.BooleanField(default=False),
        ),
    ]
