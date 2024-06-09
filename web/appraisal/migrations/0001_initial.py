# Generated by Django 5.0.6 on 2024-06-09 15:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('lat', models.CharField(max_length=255, null=True)),
                ('lon', models.CharField(max_length=255, null=True)),
                ('rooms', models.IntegerField()),
                ('floor', models.IntegerField()),
                ('housing_type', models.CharField(max_length=100)),
                ('total_area', models.FloatField()),
                ('repair', models.CharField(max_length=100)),
                ('house_type', models.CharField(max_length=100)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('city_district', models.CharField(blank=True, max_length=100, null=True)),
                ('schools', models.FloatField()),
                ('grocery_stores', models.FloatField()),
                ('kindergartens', models.FloatField()),
                ('hospitals', models.FloatField()),
                ('prediction', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]