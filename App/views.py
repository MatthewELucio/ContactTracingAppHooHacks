from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "login.html")

def logout(request):
    return render(request, "logout.html")

def help(request):
    return render(request, "help.html")

def profile(request):
    return render(request, "profile.html")

def settings(request):
    return render(request, "settings.html")