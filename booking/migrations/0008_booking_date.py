# Generated by Django 5.0.2 on 2024-04-24 07:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0007_booking_delete_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='date',
            field=models.DateField(default=datetime.date(2024, 12, 2)),
        ),
    ]
