from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from typing import *


class RegisterForm(forms.Form):
    username: str = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'User name'
        }),
        label='User name'
    )
    email: str = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        }),
        label='Email'
    )
    password1: str = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )
    password2: str = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        })
    )

    def clean_username(self) -> str:
        username: str = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this name already exists.')
        return username

    def clean_email(self) -> str:
        email: str = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean(self) -> dict:
        cleaned_data: Any = super().clean()
        password1: str = cleaned_data.get('password1')
        password2: str = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('The passwords do not match')

        return cleaned_data


class LoginForm(forms.Form):
    username: str = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'User name'
        }),
        label='User name'
    )
    password: str = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        }),
        label='Password'
    )

    def clean(self) -> dict:
        cleaned_data: Any = super().clean()
        username: str = cleaned_data.get('username')
        password: str = cleaned_data.get('password')

        if username and password:
            user: User = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Incorrect username or password')
            elif not user.is_active:
                raise forms.ValidationError('Account blocked')

        return cleaned_data
