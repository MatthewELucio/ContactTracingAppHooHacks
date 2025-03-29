import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
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
    # latest_location = LocationHistory.objects.filter(user=request.user).order_by('-recorded_at').first()
    # return render(request, 'index.html', {'latest_location': latest_location})
    return render(request, 'index.html')


def login(request):
    return render(request, "login.html")