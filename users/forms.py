from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Users


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = Users
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name']


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'email']