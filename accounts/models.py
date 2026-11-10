from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )
    specialization = models.CharField(max_length=100, blank=True, default="General Nursing")

    def __str__(self):
        return f"{self.username} ({self.role})"