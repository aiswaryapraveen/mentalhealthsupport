from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Professional1
from core.models import Goal


class SignupForm(UserCreationForm):
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES)
    age = forms.IntegerField(min_value=1)

    class Meta:
        model = CustomUser
        fields = ['username', 'email','first_name', 
                  'last_name', 'age', 'dob', 'gender','password1', 'password2', ]
        

class ProfessionalRegistrationForm(forms.ModelForm):
    class Meta:
        model = Professional1
        fields = ['qualification_details', 'qualification_document', 'experience', 'specialization']
        
        widgets = {
            'qualification_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qualification_document'].widget.attrs.update({'class': 'form-control'})

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["text"]
        widgets = {
            "text": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter a new goal"})
        }

