import os
import environ
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from .models import Code
import google.generativeai as genai



# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Google Generative AI API key
API_KEY = env('GOOGLE_GENERATIVE_AI_API_KEY')

genai.configure(api_key=API_KEY)

# Language list
lang_list = ['c', 'cpp', 'c#', 'python', 'java', 'javascript', 'css', 'dart', 'django', 'go', 'html',
             'mongodb', 'php', 'r', 'ruby', 'rust', 'sass', 'sql', 'swift', 'yaml']

def home(request):
    if request.method == "POST":
        code = request.POST['code']
        lang = request.POST['lang']

        if lang == "Select your Programming Language":
            messages.success(request, "Hey! You Forgot To Pick A Programming Language...")
            return render(request, 'home.html', {'lang_list': lang_list, 'response': code, 'code': code, 'lang': lang})
        else:
            try:
                prompt = f"""Fix this {lang} code:\n{code}\n\nRespond only with the corrected code without any code blocks. If no fix is needed, say "No fix needed"."""
                model=genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Adjust as needed for randomness
                    max_output_tokens=1000,
                    )
                )
                generated_code = response.text.strip()

                if "No fix needed" in generated_code:
                    generated_code = "No fix needed."  # Clean up the response

                record = Code(question=code, code_answer=generated_code, language=lang, user=request.user)
                record.save()
                return render(request, 'home.html', {'lang_list': lang_list, 'response': generated_code, 'lang': lang})

            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return render(request, 'home.html', {'lang_list': lang_list, 'response': code, 'code': code, 'lang': lang})

    return render(request, 'home.html', {'lang_list': lang_list})

def suggest(request):
    if request.method == "POST":
        code = request.POST['code']
        lang = request.POST['lang']

        if lang == "Select your Programming Language":
            messages.success(request, "Hey! You Forgot To Pick A Programming Language...")
            return render(request, 'suggest.html', {'lang_list': lang_list, 'response': code, 'code': code, 'lang': lang})
        else:
            try:
                prompt = f"""Generate {lang} code based on this description:\n{code}\n\nRespond only with the code, without any code blocks."""
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                    temperature=0.2,  # Adjust as needed for randomness
                    max_output_tokens=1000,
                    )
                )
                generated_code = response.text.strip()
                record = Code(question=code, code_answer=generated_code, language=lang, user=request.user)
                record.save()
                return render(request, 'suggest.html', {'lang_list': lang_list, 'response': generated_code, 'lang': lang})
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return render(request, 'suggest.html', {'lang_list': lang_list, 'response': code, 'code': code, 'lang': lang})

    return render(request, 'suggest.html', {'lang_list': lang_list})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been successfully logged in")
            return redirect('home')
        else:
            messages.error(request, "Error Logging in. Please try again!")
            return redirect('home')
    else:
        return render(request, "home.html", {})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('home')

def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "You have been registered successfully.")
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'register.html', {"form": form})

def history(request):
    if request.user.is_authenticated:
        code = Code.objects.filter(user_id=request.user.id)
        return render(request, 'history.html', {"code": code})
    else:
        messages.error(request, "You must be logged in to view history")
        return redirect('home')

def delete_history(request, history_id):
    history = Code.objects.get(pk=history_id)
    history.delete()
    messages.success(request, "Deleted successfully")
    return redirect('history')
