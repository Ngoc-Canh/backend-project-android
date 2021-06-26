from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    ROLES = (
        ("user", "User"),
        ("manager", "Manager"),
        ("admin", "Administrator"),
        ("bot", "Bot"),
    )
    name = models.CharField(choices=ROLES, max_length=10)

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    full_name = models.CharField(max_length=128)
    roles = models.ManyToManyField(Role)
    manager = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    total_dayOff = models.FloatField(default=0)


