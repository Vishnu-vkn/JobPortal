from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = "ADMIN","Admin"
        EMPLOYER="EMPLOYER","Employer"
        CANDIDATE="CANDIDATE","Candidate"

    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15,blank=True)

    role=models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE
    )

    is_verified=models.BooleanField(default=False)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    