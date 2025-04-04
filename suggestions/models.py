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
class Meditation(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    audio_file = models.FileField(upload_to="meditation_audios/", blank=True, null=True)
    text_guide = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

class UserMeditation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meditation = models.ForeignKey(Meditation, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.meditation.title}"