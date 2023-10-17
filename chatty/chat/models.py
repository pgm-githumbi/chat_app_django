from django.utils import timezone
from django.db import models

# Create your models here.


class Room(models.Model):
    room_name = models.CharField(max_length=256,unique=True,)
    created_at = models.DateTimeField(default=timezone.now,)
    
class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)


class Message(models.Model):
    room = models.ForeignKey(Room, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    message_body = models.TextField(max_length=355, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
