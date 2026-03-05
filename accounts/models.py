from django.db import models
from django.contrib.auth.models import User

REGION_CHOICES = [
    ('NA', 'North America'),
    ('EU', 'Europe'),
    ('AS', 'Asia'),
    ('SA', 'South America'),
    ('AF', 'Africa'),
    ('OC', 'Oceania'),
    ('ME', 'Middle East'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = models.CharField(max_length=2, choices=REGION_CHOICES, default='NA')

    def __str__(self):
        return f"{self.user.username} - {self.region}"