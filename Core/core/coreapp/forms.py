from django import forms
from .models import CoreUser


class LoginForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':' Username', 'id': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':' Password', 'id': 'password'}))
    class  Meta:
        model = CoreUser
        fields = ['username', 'password']


class SignupForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':' Username', 'id': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':' Password', 'id': 'password'}))
    email = forms.EmailField(widget = forms.TextInput(attrs = {'placeholder':' Email', 'id': 'email'}))
    class  Meta:
        model = CoreUser
        fields = ['username', 'password', 'email']
    				