from django import forms
from .models import Post, Reply

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Share your thoughts...'}))

    class Meta:
        model = Post
        fields = ['content']

from django import forms
from .models import Reply

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a reply...', 'rows': 2}),
        }


