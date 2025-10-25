from django.contrib import admin
from .models import ChatMessage, ChatSession, CustomUser

# Register your models here.
admin.site.register(ChatMessage)
admin.site.register(ChatSession)
admin.site.register(CustomUser)