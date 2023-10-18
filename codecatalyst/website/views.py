from django.shortcuts import render, redirect
from django.contrib import messages
import openai
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm
from .models import Code


# Create your views here.


def home(request):
    lang_list = ['c', 'cpp','c#','python','java', 'javascript',  'css', 'dart', 'django', 'go', 'html', 
                 'mongodb','php', 'r','ruby', 'rust', 'sass', 'sql', 'swift', 'yaml']

    if request.method == "POST":
        code = request.POST['code']
        lang = request.POST['lang']

        # Check to make sure they picked a lang
        if lang == "Select your Programming Language":
            messages.success(
                request, "Hey! You Forgot To Pick A Programming Language...")
            return render(request, 'home.html', {'lang_list': lang_list, 'response': code, 'code': code, 'lang': lang})
        else:
            # OpenAI Key
            # openai.api_key = "***************ENTER YOURS OPENAI API KEY***************"
            openai.api_key = "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"
            # Create OpenAI Instance
            openai.Model.list()
            # Make an OpenAI Request
            try:
                response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=f"Respond only with code. Fix this {lang} code: {code}",
                    temperature=0,
                    max_tokens=1000,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                )
                # parse the response
                response = (response["choices"][0]["text"]).strip()
                # Save the response to databases...
                record = Code(question=code, code_answer=response,
                              language=lang, user=request.user)
                record.save()
                return render(request, 'home.html', {'lang_list': lang_list, 'response': response, 'lang': lang})

            except Exception as e:
                return render(request, 'home.html', {'lang_list': lang_list, 'response': e, 'lang': lang})

    return render(request, 'home.html', {'lang_list': lang_list})


def suggest(request):
    lang_list = ['c', 'cpp','c#','python','java', 'javascript',  'css', 'dart', 'django', 'go', 'html', 
                 'mongodb','php', 'r','ruby', 'rust', 'sass', 'sql', 'swift', 'yaml']
    if request.method == "POST":
        code = request.POST['code']
        lang = request.POST['lang']

        # Check to make sure they picked a lang
        if lang == "Select your Programming Language":
            messages.success(
                request, "Hey! You Forgot To Pick A Programming Language...")
            return render(request, 'suggest.html', {'lang_list': lang_list, 'response': code, 'code': code, 'lang': lang})
        else:
            # OpenAI Key
            openai.api_key = "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"
            # Create OpenAI Instance
            openai.Model.list()
            # Make an OpenAI Request
            try:
                response = openai.Completion.create(
                    engine='text-davinci-003',
                    prompt=f"Respond only with code. {code}",
                    temperature=0,
                    max_tokens=1000,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                )
                # parse the response
                response = (response["choices"][0]["text"]).strip()
                # save the response to  database
                record = Code(question=code, code_answer=response,
                              language=lang, user=request.user)
                record.save()
                return render(request, 'suggest.html', {'lang_list': lang_list, 'response': response, 'lang': lang})

            except Exception as e:
                return render(request, 'suggest.html', {'lang_list': lang_list, 'response': e, 'lang': lang})

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
            messages.success(request, "Error Logging in. Please try again!")
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
        messages.success(request, "You must be logged in to view history ")
        return redirect('home')


def delete_history(request, history_id):
    history = Code.objects.get(pk=history_id)
    history.delete()
    messages.success(request, "deleted successfully")
    return redirect('history')
