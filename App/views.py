from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        notifications = None #update once we have data structure in models
        return render(request, "index.html", {'Notifications':notifications})
    else: return render(request, "login.html")

def report_illness(request):
    if request.user.is_authenticated:
        return render(request, "report.html")
    else: return render(request, "login.html")

def learn(request):
    if request.user.is_authenticated:
        return render(request, "learn.html")
    else: return render(request, "login.html")

def notify(request):
    if request.user.is_authenticated:
        return render(request, "notify.html")
    else: return render(request, "login.html")

def login(request):
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return login(request)

def home(request):
    if request.user.is_authenticated:
        return render(request, "home.html", {'email': request.user.email}) 
    else: return render(request, "login.html")

def help(request):
    return render(request, "help.html")


def profile(request):
    if request.user.is_authenticated:
        return render(request, "profile.html")
    else: return render(request, "login.html")

def settings(request):
    if request.user.is_authenticated:
        return render(request, "settings.html")

@login_required
def home(request):
    if request.user.is_authenticated:
        return render(request, "home.html", {'email': request.user.email}) 
    else: return render(request, "login.html")