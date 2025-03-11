from django.db import models
from django.conf import settings

class JournalEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    mental_health_status = models.CharField(max_length=255, blank=True, null=True)  # Stores ML result
    sentiment = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Journal Entry by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"

class Goal(models.Model):
    text = models.CharField(max_length=255)  

    def __str__(self):
        return self.text

class DailyGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)  
    completed = models.BooleanField(default=False)  # Track completion status

    class Meta:
        unique_together = ('user', 'goal', 'date')

from django.db import models
from django.conf import settings

class PersonalGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=255)  # Goal description
    date = models.DateField(auto_now_add=True)  # When the goal was set
    completed = models.BooleanField(default=False)  # Track completion status

    def __str__(self):
        return f"{self.text} ({'Completed' if self.completed else 'Pending'})"
