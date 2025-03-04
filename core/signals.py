from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser

@receiver(post_save, sender=CustomUser)
def create_professional_profile(sender, instance, created, **kwargs):
    # Remove the automatic creation of ProfessionalProfile
    pass
