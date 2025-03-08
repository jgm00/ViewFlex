from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    followings = models.ManyToManyField('self', symmetrical=False, related_name='followers')

from django.db import models
from django.conf import settings

class Survey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferred_genres = models.JSONField(default=list) 
    viewing_reason = models.CharField(max_length=50)
    viewing_with = models.CharField(max_length=50)
    favorite_actor = models.CharField(max_length=100, blank=True)
    movie_elements = models.JSONField(default=list) 
    favorite_movies = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Survey"