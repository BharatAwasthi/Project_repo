from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import speech_recognition as sr
import webbrowser
import os
import pyttsx3
import threading

# Import your forms
from .forms import SignUpForm, LoginForm

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Use threading to handle TTS operations asynchronously
tts_lock = threading.Lock()

def say(text):
    print(f"Saying: {text}")  # Debugging statement
    def speak():
        global tts_lock
        with tts_lock:
            engine.say(text)
            engine.runAndWait()
    thread = threading.Thread(target=speak)
    thread.start()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        print("Listening...")
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand what you said.")
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def open_website(command):
    print(f"Trying to open website for command: {command}")  # Debugging statement
    sites = {
        "youtube": "www.youtube.com",
        "wikipedia": "www.wikipedia.com"
    }
    for site, url in sites.items():
        if f"open {site}" in command.lower():
            print(f"Opening {site}: {url}")
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"Failed to open: {e}")  # Debugging statement
                
            say(f"Opening {site}")
            return True
    return False

def open_application(app_name):
    print(f"Trying to open application: {app_name}")  # Debugging statement
    if app_name.lower() == "this pc":
        os.startfile("explorer.exe")
        say("Opening This PC")
        return True
    elif app_name.lower() == "notepad":
        os.startfile("notepad.exe")
        say("Opening Notepad")
        return True
    elif app_name.lower() == "calculator":
        os.startfile("calc.exe")
        say("Opening Calculator")
        return True
    elif app_name.lower() == "camera":
        os.startfile("microsoft.windows.camera:")
        say("Opening Camera")
        return True
    # Add more applications as needed
    return False

def interpret_command(command):
    print(f"Interpreting command: {command}")  # Debugging statement
    greetings = ["hello", "hi", "hey"]
    for greeting in greetings:
        if greeting in command.lower():
            say("Hello, I am fine.")
            return
    
    if "who created you" in command.lower():
        say("I was created by Aj.")
        return
    
    if open_website(command):
        return
    if open_application(command):
        return
    say(f"Command not recognized: {command}")

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')  # Redirect to the home page or any other page
    else:
        form = SignUpForm()
    return render(request, 'home/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to the home page or any other page
    else:
        form = LoginForm()
    return render(request, 'home/login.html', {'form': form})

def home_view(request):
    return render(request, 'home/home.html')

@csrf_exempt
def speak_view(request):
    if request.method == "POST":
        print("POST request received")  # Debugging statement
        command = take_command()
        print(f"Command received: {command}")  # Debugging statement
        interpret_command(command)
        return JsonResponse({"message": "Command executed"})
    print("Invalid request method")  # Debugging statement
    return JsonResponse({"error": "Invalid request method"}, status=400)


def demo_request_view(request):
    return render(request, 'home/demo.html')
