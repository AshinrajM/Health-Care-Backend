# Generated by Django 5.0.2 on 2024-03-30 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0003_rename_is_mrng_available_is_morning'),
    ]

    operations = [
        migrations.AlterField(
            model_name='available',
            name='date',
            field=models.DateField(unique=True),
        ),
    ]
