from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Professional1, ProfessionalDetails
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

class ProfessionalDetailsForm(forms.ModelForm):
    class Meta:
        model = ProfessionalDetails
        fields = ['bio', 'profile_picture', 'location', 'phone', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write a short bio...'}),
            'location': forms.TextInput(attrs={'placeholder': 'Your location'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Contact number'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})
from django import forms
from .models import CustomUser, Professional1, ProfessionalDetails

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'age', 'dob', 'gender']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

class Professional1Form(forms.ModelForm):
    class Meta:
        model = Professional1
        fields = ['qualification_details', 'qualification_document', 'experience', 'specialization']

class ProfessionalDetailsForm(forms.ModelForm):
    class Meta:
        model = ProfessionalDetails
        fields = ['profile_picture', 'bio', 'location', 'phone', 'website']
from .models import ProfessionalReview

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProfessionalReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, '⭐' * i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Leave your feedback...'}),
        }

from django.contrib.auth.forms import PasswordChangeForm

class CustomChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Current Password", widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
