from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser




@login_required
def chat_page(request):
    return render(request, 'chat.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password')
            print(name,pwd)
            user=authenticate(request, username=name, password=pwd)
            if user is not None:
                auth_login(request, user)
                return redirect('chat_page')  
            else:
                form.add_error(None, 'Username or password is not correct')
                return redirect('/')

    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        emailid = request.POST.get('email')
        pwd = request.POST.get('password')

        if CustomUser.objects.filter(username=name).exists():
            return render(request, 'signup.html', {'error': 'Username already taken'})

        if CustomUser.objects.filter(email=emailid).exists():
            return render(request, 'signup.html', {'error': 'Email already registered'})

        my_user = CustomUser.objects.create_user(username=name, email=emailid, password=pwd)
        my_user.save()
        
        return redirect('login')

    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('login')