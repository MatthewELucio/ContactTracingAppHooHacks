import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import LocationHistory

# Create your views here.
@csrf_exempt
@require_POST
def update_location(request):
    try:
        data = json.loads(request.body)
        latitude = data['latitude']
        longitude = data['longitude']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    
    # Save the location history for the logged-in user.
    # Make sure the 'user' field in LocationHistory is uncommented.
    loc = LocationHistory.objects.create(
        user=request.user,
        latitude=latitude,
        longitude=longitude
    )
    
    return JsonResponse({
        'status': 'success',
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'recorded_at': loc.recorded_at.isoformat()
    })

def index(request):
    if request.user.is_authenticated:
        return render(request, "index.html")
    else: return render(request, "login.html")
    # latest_location = LocationHistory.objects.filter(user=request.user).order_by('-recorded_at').first()
    # return render(request, 'index.html', {'latest_location': latest_location})
    return render(request, 'index.html')


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
    return render(request, "home.html", {'email': request.user.email}) 
    else: return render(request, "login.html")