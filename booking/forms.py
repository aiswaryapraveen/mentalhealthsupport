from django import forms
from django.db import models
from .models import Availability

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['date', 'start_time', 'end_time', 'max_capacity']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'max_capacity': forms.NumberInput(attrs={'min': 1, 'max': 10}),  # Limit for safety
        }


class BookingForm(forms.Form):
    date = forms.DateField(widget=forms.Select(), required=True)
    availability_id = forms.ModelChoiceField(
        queryset=Availability.objects.none(),
        empty_label="Select a time slot",
        required=True
    )

    def __init__(self, *args, professional=None, **kwargs):
        super().__init__(*args, **kwargs)
        if professional:
            # Get available slots
            available_slots = Availability.objects.filter(
                professional=professional,
                booked_count__lt=models.F('max_capacity')
            ).order_by('date', 'start_time')

            # Populate date choices
            unique_dates = sorted(set(slot.date for slot in available_slots))
            self.fields['date'].widget.choices = [(date, date) for date in unique_dates]

            # Populate time slots (Initially empty, will be updated via JavaScript)
            self.fields['availability_id'].queryset = available_slots