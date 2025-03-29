from django.shortcuts import render
from django.template import loader

# Create your views here.
def index(request):
    template = loader.get_template("App/index.html")
    return render(request, "App/index.html")

def login(request):
    template = loader.get_template("App/login.html")
    return render(request, "App/login.html")