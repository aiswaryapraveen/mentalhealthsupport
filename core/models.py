from django.db import models
from django.conf import settings

class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # mental_health_status = models.CharField(max_length=255, blank=True, null=True)  # Stores ML result

    def __str__(self):
        return f"Journal Entry by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"
