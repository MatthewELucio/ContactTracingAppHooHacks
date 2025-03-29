import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .models import LocationHistory

# Create your views here.


def index(request):
    return render(request, "index.html")

def login(request):
    return render(request, "login.html")