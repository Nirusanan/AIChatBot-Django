from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, ChatMessage, ChatSession
from django.utils import timezone
from dotenv import load_dotenv
import os
from groq import Groq

# Load the environment variables from .env file
load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


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


conversations = []
new_chat_state = True
chat_session = None


def get_chat_sessions(request):
    sessions = ChatSession.objects.all().order_by('-updated_at')  # '-' indicates descending order

    # Construct a list of dictionaries for each session
    data = [
        {'chat_uuid': session.chat_uuid, 'chat_title': session.chat_title, 'updated_at': session.updated_at}
        for session in sessions
    ]

    return JsonResponse(data, safe=False)  # safe=False is necessary to serialize a list


def get_chat_messages(request, chat_uuid):
    global conversations, new_chat_state, chat_session
    # Retrieve the ChatSession by its UUID
    chat_session = get_object_or_404(ChatSession, chat_uuid=chat_uuid)

    # Retrieve all messages linked to the ChatSession
    messages = ChatMessage.objects.filter(chat=chat_session).order_by('time_stamp')

    # Create a list to store the formatted messages
    conversations = []

    # Format each message pair into the specified JSON structure
    for message in messages:
        conversations.append({"role": "user", "content": message.user_input})
        conversations.append({"role": "assistant", "content": message.response})

    new_chat_state = False

    # Return the conversation list as a JSON response
    return JsonResponse({"conversation": conversations})


def chat_response(request):
    global conversations, new_chat_state, chat_session
    if request.method == 'POST':

        user_input = request.POST.get('message', '')

        if user_input == 'New chat':
            conversations = []
            new_chat_state = True

            return JsonResponse({'response': ""})

        else:
            if new_chat_state:
                conversations.append({"role": "user", "content": user_input})

                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=conversations,
                )

                assistant_response = response.choices[0].message.content

                conversations.append({"role": "assistant", "content": assistant_response})

                title_response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user",
                               "content": f"""Generate a concise title for this {user_input} - Ensure that the title is in English and does not include quotation marks. And you do not tell any describe of your title, just give the title"""}]
                )

                # Create a new ChatSession
                chat_title = title_response.choices[0].message.content
                chat_session = ChatSession(chat_title=chat_title, updated_at=timezone.now())
                chat_session.save()

                # Create a new ChatMessage linked to the ChatSession
                chat_message = ChatMessage(chat=chat_session, user_input=user_input, response=assistant_response)
                chat_message.save()

                new_chat_state = False
                return JsonResponse({'response': assistant_response})

            else:
                print("Old chat session!")
                conversations.append({"role": "user", "content": user_input})

                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=conversations,
                )

                assistant_response = response.choices[0].message.content

                conversations.append({"role": "assistant", "content": assistant_response})

                # Create a new ChatMessage linked to the ChatSession
                chat_message = ChatMessage(chat=chat_session, user_input=user_input, response=assistant_response)
                chat_message.save()

                return JsonResponse({'response': assistant_response})
