from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="Prefer not to say")
    is_professional = models.BooleanField(default=False)  

    def __str__(self):
        return self.username



class Professional1(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qualification_details = models.TextField(blank=True, null=True)
    qualification_document = models.FileField(upload_to='document/', blank=True, null=True)
    experience = models.IntegerField(default=0)  # Years of experience
    specialization = models.CharField(max_length=255, blank=True, null=True)
    is_approved = models.BooleanField(null=True, blank=True)  # Admin-controlled

    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.is_approved else 'Pending Approval'}"
    


