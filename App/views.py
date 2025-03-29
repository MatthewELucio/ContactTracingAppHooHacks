from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "login.html")

def logout(request):
    return render(request, "logout.html")

@login_required
def home(request):
    return render(request, "home.html", {'email': request.user.email}) 

def help(request):
    return render(request, "help.html")

def profile(request):
    return render(request, "profile.html")

def settings(request):
    return render(request, "settings.html")