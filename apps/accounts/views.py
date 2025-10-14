from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from typing import (
    Any,
)
from django.http import (
    HttpRequest,
    HttpResponse,
)


def register_page(
        request: HttpRequest
    ) -> HttpResponse:
    """
    Displaying the registration page

    Params:
     - request: HttpRequest
    Return: 
     - response: HttpResponse
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form: Any = RegisterForm(request.POST)
        if form.is_valid():
            username: str = form.cleaned_data['username']
            email: str = form.cleaned_data['email']
            password: str = form.cleaned_data['password1']

            user = User.objects.create_user(
                username=username, 
                email=email,
                password=password
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form: Any = RegisterForm()
    return render(
        request, 
        'register.html', 
        {'form': form}
    )


def login_page(
        request: HttpRequest
        ) -> HttpResponse:
    """
    Displaying the login page

    Params:
     - request: HttpRequest
    Return: 
     - response: HttpResponse
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form: Any = LoginForm(request.POST)
        if form.is_valid():
            username: str = form.cleaned_data['username']
            password: str = form.cleaned_data['password']

            user = authenticate(
                username=username, 
                password=password
            )
            
            if user is not None:
                login(request, user)
                messages.info(request, f'Welcome, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Incorrect username or password.')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form: Any = LoginForm()
    return render(
        request,
        'login.html',
        {'form': form}
    )

def logout_view(
        request: HttpRequest
        ) -> HttpResponse:
    """
    User logout

    Params:
     - request: HttpRequest
    Return: 
     - response: HttpResponse
    """
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

def home(
        request: HttpRequest
        ) -> HttpResponse:
    """
    Home page

    Params:
     - request: HttpRequest
    Return: 
     - response: HttpResponse
    """
    return render(request, 'home.html')

@login_required
def profile(
    request: HttpRequest
    ) -> HttpResponse:

    """
    User profile

    Params:
     - request: HttpRequest
    Return: 
     - response: HttpResponse
    """
    return render(
        request, 
        'profile.html', 
        {'user': request.user}
    )