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
from .tools import weather_function, internet_search, get_weather, fetch_text_results
import json
from openai import OpenAI
import copy

# Load the environment variables from .env file
load_dotenv()

current_model = "openai/gpt-oss-20b"
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
openAI_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


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


@login_required
def get_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at') # '-' indicates descending order

    # Construct a list of dictionaries for each session
    data = [
        {'chat_uuid': session.chat_uuid, 'chat_title': session.chat_title, 'updated_at': session.updated_at}
        for session in sessions
    ]

    return JsonResponse(data, safe=False)  # safe=False is necessary to serialize a list


@login_required
def get_chat_messages(request, chat_uuid):
    global conversations, new_chat_state, chat_session
    # Retrieve the ChatSession by its UUID
    chat_session = get_object_or_404(ChatSession, chat_uuid=chat_uuid)

    # Retrieve all messages linked to the ChatSession
    messages = ChatMessage.objects.filter(chat=chat_session).order_by('time_stamp')

    # Create a list to store the formatted messages
    conversations = [{"role": "system", "content": "You are a helpful assistant"}]

    # Format each message pair into the specified JSON structure
    for message in messages:
        conversations.append({"role": "user", "content": message.user_input})
        conversations.append({"role": "assistant", "content": message.response})

    new_chat_state = False

    # Return the conversation list as a JSON response
    return JsonResponse({"conversation": conversations})


@login_required
def chat_response(request):
    global conversations, new_chat_state, chat_session, copy_conversations
    if request.method == 'POST':

        user_input = request.POST.get('message', '')

        if user_input == 'New chat':
            conversations = [{"role": "system", "content": "You are a helpful assistant"}]
            new_chat_state = True

            return JsonResponse({'response': ""})

        else:
            if new_chat_state:
                conversations.append({"role": "user", "content": user_input})

                # Groq
                if current_model=="openai/gpt-oss-20b":

                    response = groq_client.chat.completions.create(
                        model=current_model,
                        messages=conversations,
                        tools=[weather_function, internet_search], 
                        tool_choice="auto",
                    )

                    message = response.choices[0].message

                    # Tool calling
                    if message.tool_calls:
                        available_functions = {
                            "get_weather": get_weather,
                            "fetch_text_results": fetch_text_results,
                        }

                        for tool_call in message.tool_calls:
                    
                            function_name = tool_call.function.name
                            function_to_call = available_functions.get(function_name)

                            if not function_to_call:
                                print("Unknown function:", function_name)
                                continue

                            # parse the function arguments safely
                            try:
                                function_args = json.loads(tool_call.function.arguments)
                            except Exception as e:
                                function_args = {}
                                print("Failed to parse function arguments:", e)

                            # call the function
                            if function_name == "get_weather":
                                function_response = function_to_call(city=function_args.get("location"))
                            elif function_name == "fetch_text_results":
                                function_response = function_to_call(query=function_args.get("query"))
                            else:
                                function_response = function_to_call(**function_args)

                            # Ensure the function response stored as a plain string
                            if isinstance(function_response, (dict, list)):
                                function_content = json.dumps(function_response)  # for structured data
                            else:
                                function_content = str(function_response)

                            copy_conversations = copy.deepcopy(conversations)
                            copy_conversations.append(
                                {
                                    "role": "function",
                                    "name": function_name,
                                    "content": function_content,
                                }
                            )
                        

                        tool_response = groq_client.chat.completions.create(
                            model=current_model,
                            messages=copy_conversations,
                        )
                
                        assistant_response = tool_response.choices[0].message.content
                
                    else:
                        assistant_response = message.content

                # OpenAI
                else:
                    response = openAI_client.responses.create(
                        model=current_model,
                        tools=[{"type": "web_search"}],
                        input=conversations
                    )

                    assistant_response = response.output_text


                conversations.append({"role": "assistant", "content": assistant_response})

                title_prompt = """
                    Generate a short, concise English title (maximum 5 words) for the following user input:
                    "{user_input}"

                    Rules:
                    - Keep it simple and descriptive.
                    - Avoid punctuation and quotation marks.
                    - No explanations or extra text.
                    Return only the title.
                """

                if current_model == "openai/gpt-oss-20b":
                    title_response = groq_client.chat.completions.create(
                        model=current_model,
                        messages=[{"role": "user",
                                "content": title_prompt.format(user_input=user_input)
                        }]
                    )
                    chat_title = title_response.choices[0].message.content
                
                else:
                    title_response = openAI_client.responses.create(
                        model=current_model,
                        input=[{"role": "user",
                                "content": title_prompt.format(user_input=user_input)
                        }]
                    )
                    chat_title = title_response.output[0].content[0].text


                # Create a new ChatSession
                chat_session = ChatSession.objects.create(
                    user=request.user,
                    chat_title=chat_title,
                    updated_at=timezone.now()
                )

                # Create a new ChatMessage linked to the ChatSession
                ChatMessage.objects.create(
                    chat=chat_session,
                    user=request.user,
                    user_input=user_input,
                    response=assistant_response
                )

                new_chat_state = False
                return JsonResponse({'response': assistant_response, 'new_chat_session': chat_session.chat_uuid})

            else:
                print("Old chat session!")
                conversations.append({"role": "user", "content": user_input})

                # Groq
                if current_model=="openai/gpt-oss-20b":
                    response = groq_client.chat.completions.create(
                        model=current_model,
                        messages=conversations,
                        tools=[weather_function, internet_search], 
                        tool_choice="auto",
                    )

                    message = response.choices[0].message

                    # Tool calling
                    if message.tool_calls:
                        available_functions = {
                            "get_weather": get_weather,
                            "fetch_text_results": fetch_text_results,
                        }

                        for tool_call in message.tool_calls:
                    
                            function_name = tool_call.function.name
                            function_to_call = available_functions.get(function_name)

                            if not function_to_call:
                                print("Unknown function:", function_name)
                                continue

                            # parse the function arguments safely
                            try:
                                function_args = json.loads(tool_call.function.arguments)
                            except Exception as e:
                                function_args = {}
                                print("Failed to parse function arguments:", e)

                            # call the function
                            if function_name == "get_weather":
                                function_response = function_to_call(city=function_args.get("location"))
                            elif function_name == "fetch_text_results":
                                function_response = function_to_call(query=function_args.get("query"))
                            else:
                                function_response = function_to_call(**function_args)

                            # Ensure the function response stored as a plain string
                            if isinstance(function_response, (dict, list)):
                                function_content = json.dumps(function_response)  # for structured data
                            else:
                                function_content = str(function_response)

                            copy_conversations = copy.deepcopy(conversations)
                            copy_conversations.append(
                                {
                                    "role": "function",
                                    "name": function_name,
                                    "content": function_content,
                                }
                            )

                        tool_response = groq_client.chat.completions.create(
                            model=current_model,
                            messages=copy_conversations,
                        )
                
                        assistant_response = tool_response.choices[0].message.content
                    
                    else:
                        assistant_response = message.content

                # OpenAI
                else:
                    response = openAI_client.responses.create(
                        model=current_model,
                        tools=[{"type": "web_search"}],
                        input=conversations
                    )

                    assistant_response = response.output_text

                conversations.append({"role": "assistant", "content": assistant_response})

                # Create a new ChatMessage linked to the ChatSession
                ChatMessage.objects.create(
                    chat=chat_session,
                    user=request.user,
                    user_input=user_input,
                    response=assistant_response
                )

                 # Update session timestamp
                chat_session.updated_at = timezone.now()
                chat_session.save(update_fields=["updated_at"])

                return JsonResponse({'response': assistant_response, 'old_chat_session': chat_session.chat_uuid})

@login_required
def delete_chat(request, chat_uuid):
    global chat_session
    # Retrieve the ChatSession by its UUID
    chat_session = get_object_or_404(ChatSession, chat_uuid=chat_uuid)
    if request.method == 'DELETE':
        try:
            ChatMessage.objects.filter(chat=chat_session).delete()
            ChatSession.objects.filter(chat_uuid=chat_uuid).delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def change_model(request):
    global current_model
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            selected_model = data.get("model")
            
            # validation
            allowed_models = [
                "openai/gpt-oss-20b",
                "gpt-4o",
                "gpt-4.1",
                "gpt-4.1-mini",
            ]

            if selected_model not in allowed_models:
                return JsonResponse({"message": "Invalid model selection"}, status=400)

            current_model = selected_model
            return JsonResponse({"message": f"✅ Model changed to {current_model}"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    return JsonResponse({"message": "Only POST requests are allowed"}, status=405)

@login_required
def rename_chat(request, chat_uuid):
    if request.method == "POST":
        data = json.loads(request.body)
        new_title = data.get("title")

        try:
            chat = ChatSession.objects.get(chat_uuid=chat_uuid)
            chat.chat_title = new_title
            chat.save()
            return JsonResponse({"success": True, "new_title": new_title})
        except chat.DoesNotExist:
            return JsonResponse({"success": False, "error": "Chat not found"}, status=404)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
