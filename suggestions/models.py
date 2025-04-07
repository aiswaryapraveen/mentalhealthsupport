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
class BubbleGameRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']  # highest scores first

    def __str__(self):
        return f"{self.user.username} - {self.score}"

class MemoryGameScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    time_taken = models.IntegerField(null=True, blank=True)  # in seconds
    attempts = models.IntegerField(null=True, blank=True)
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}"
class FocusMazeScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    time_taken = models.FloatField(help_text="Time taken in seconds")
    date_played = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.time_taken}s"
class YogaSession(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=20)
    video_url = models.URLField(blank=True, null=True)  # Optional for embedding

    def __str__(self):
        return self.title
class YogaCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(YogaSession, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.session.title}"