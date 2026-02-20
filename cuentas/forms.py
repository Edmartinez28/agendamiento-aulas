# forms.py
from django import forms
from .models import User

class AvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar"]