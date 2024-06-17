# Generated by Django 5.0.2 on 2024-06-12 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0016_alter_available_status_alter_booking_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='available',
            name='status',
            field=models.CharField(choices=[('active', 'active'), ('booked', 'booked'), ('asociate_blocked and cancelled', 'asociate_blocked and cancelled')], default='active', max_length=100),
        ),
    ]