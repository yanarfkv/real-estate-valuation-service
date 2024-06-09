from django.db import models
from django.contrib.auth.models import User


class Property(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=255)
    lat = models.CharField(null=True, max_length=255)
    lon = models.CharField(null=True, max_length=255)

    rooms = models.IntegerField()
    floor = models.IntegerField()
    housing_type = models.CharField(max_length=100)
    total_area = models.FloatField()
    repair = models.CharField(max_length=100)
    house_type = models.CharField(max_length=100)

    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city_district = models.CharField(max_length=100, null=True, blank=True)

    schools = models.FloatField()
    grocery_stores = models.FloatField()
    kindergartens = models.FloatField()
    hospitals = models.FloatField()

    prediction = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
