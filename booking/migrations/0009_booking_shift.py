# Generated by Django 5.0.2 on 2024-04-24 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_booking_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='shift',
            field=models.CharField(blank=True, default='morning', max_length=20, null=True),
        ),
    ]
