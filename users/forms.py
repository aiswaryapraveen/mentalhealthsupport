from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignupForm(UserCreationForm):
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=CustomUser.GENDER_CHOICES)
    age = forms.IntegerField(min_value=1)

    class Meta:
        model = CustomUser
        fields = ['username', 'email','first_name', 
                  'last_name', 'age', 'dob', 'gender','password1', 'password2', ]
