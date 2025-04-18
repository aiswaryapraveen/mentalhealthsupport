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
    
class ProfessionalDetails(models.Model):
    professional = models.OneToOneField(Professional1, on_delete=models.CASCADE, related_name='details')

    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.professional.user.username}'s Profile Details"
class ProfessionalReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional1, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.professional.user.username} ({self.rating}⭐)"