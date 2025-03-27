from django.urls import path, include
from .views import chat_page, login_view, signup_view, logout_view, get_chat_sessions, get_chat_messages, chat_response 
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(chat_page), name='chat_page'),
    path('login/', login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path('logout/', logout_view, name='logout'),
    path('api/chat_id_title/', get_chat_sessions, name='get_all_chats_id_title'),
    path('api/chat/<uuid:chat_uuid>/', get_chat_messages, name='chat_details_api'),
    path('api/chat/', chat_response, name='chat_api')
]