from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required



@login_required
def chat_page(request):
    return render(request, 'chat.html')

def login_view(request):
    template = loader.get_template('login.html')
    return HttpResponse(template.render())

def signout(request):
    return 

def signup_view(request):
    template = loader.get_template('signup.html')
    return HttpResponse(template.render())