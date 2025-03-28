from django.db import models
from django.conf import settings

class SelfAffirmation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    accomplishments = models.TextField()
    strengths = models.TextField()
    positive_message = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"
