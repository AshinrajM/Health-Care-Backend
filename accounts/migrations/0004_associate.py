# Generated by Django 5.0.2 on 2024-02-15 18:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Associate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experience', models.CharField(blank=True, max_length=50, null=True)),
                ('certificate_no', models.CharField(blank=True, max_length=50, null=True)),
                ('fee_per_hour', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('age', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
