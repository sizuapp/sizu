from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class UploadPDFForm(forms.Form):
    pdf_file = forms.FileField(label="Sube tu material de estudio (PDF)", required=True)