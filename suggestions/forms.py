from django import forms
from .models import Meditation

class MeditationForm(forms.ModelForm):
    class Meta:
        model = Meditation
        fields = ['title', 'description', 'duration', 'audio_file', 'text_guide']
