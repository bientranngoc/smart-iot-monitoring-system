"""
Base IoT models - User and Device (MySQL)
"""

from django.db import models


class User(models.Model):
    """IoT User model"""
    username = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


class Device(models.Model):
    """IoT Device model"""
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'devices'
    
    def __str__(self):
        return f"{self.name} (User: {self.user.username})"
