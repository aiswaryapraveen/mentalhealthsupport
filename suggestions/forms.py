from django import forms
from .models import Meditation, YogaSession

class MeditationForm(forms.ModelForm):
    class Meta:
        model = Meditation
        fields = ['title', 'description', 'duration', 'audio_file', 'text_guide']
class YogaSessionForm(forms.ModelForm):
    class Meta:
        model = YogaSession
        fields = ['title', 'description', 'duration', 'video_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 20 min'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control'}),
        }