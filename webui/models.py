from django.db import models

# Create your models here.
class Tweet(models.Model):
    status_id = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    content = models.CharField(max_length=255)
