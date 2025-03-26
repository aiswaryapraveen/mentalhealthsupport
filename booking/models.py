from django.db import models
from users.models import Professional1  # Import the existing Professional1 model
from django.conf import settings

class Availability(models.Model):
    professional = models.ForeignKey(Professional1, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)  # Mark if the slot is booked
    max_capacity = models.PositiveIntegerField(default=1)  # Max number of people per slot
    booked_count = models.PositiveIntegerField(default=0)  # Track number of bookings

    def is_full(self):
        return self.booked_count >= self.max_capacity  # Check if the slot is full

    def __str__(self):
        return f"{self.professional.user.username} - {self.date} {self.start_time} to {self.end_time}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Client
    professional = models.ForeignKey(Professional1, on_delete=models.CASCADE)  # Professional being booked
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)  # Selected time slot
    booked_at = models.DateTimeField(auto_now_add=True)  # Timestamp when booked
    status_choices = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')

    def __str__(self):
        return f"Booking by {self.user.username} with {self.professional.user.username} on {self.availability.date} ({self.availability.start_time} - {self.availability.end_time})"
