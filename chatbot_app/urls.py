from django.urls import path, include
from .views import chat_page, login_view, signup_view, signout
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(chat_page), name='chat_page'),
    path('login/', login_view, name="login"),
    path("signup", signup_view, name="signup"),
    path('signout', signout, name='signout'),
]