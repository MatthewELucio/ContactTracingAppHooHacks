from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import json
import math
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import LocationHistory, RelevantLocation
import django.utils.timezone as timezone


def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance in meters between two points on Earth."""
    R = 6371000  # Radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@csrf_exempt
@require_POST
@login_required
def update_location(request):
    try:
        data = json.loads(request.body)
        latitude = data['latitude']
        longitude = data['longitude']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    
    # Create a new location history record, associating it with the logged-in user.
    location_entry = LocationHistory.objects.create(
        user=request.user,  # Ensure that the user field is uncommented in your model.
        latitude=latitude,
        longitude=longitude
    )
    
    now = timezone.now()
    RADIUS_THRESHOLD = 50         # in meters (adjust as needed)
    TIME_THRESHOLD = 30 * 60

    latest_relevant = RelevantLocation.objects.filter(user=request.user).order_by('-end_time').first()

    if latest_relevant:
        # Compute distance from the new location to the relevant location's stored coordinates.
        distance = haversine(latest_relevant.latitude, latest_relevant.longitude, latitude, longitude)
        if distance <= RADIUS_THRESHOLD:
            # If within the threshold, update the end_time.
            latest_relevant.end_time = now
            latest_relevant.save()
        else:
            # If outside the threshold, check if the duration meets the time threshold.
            duration = (latest_relevant.end_time - latest_relevant.start_time).total_seconds()
            if duration < TIME_THRESHOLD:
                # If not enough time has passed, you may choose to discard it.
                latest_relevant.delete()
            # In either case, start a new relevant location record.
            RelevantLocation.objects.create(
                user=request.user,
                latitude=latitude,
                longitude=longitude,
                start_time=now,
                end_time=now
            )
    else:
        # No relevant location exists; create one.
        RelevantLocation.objects.create(
            user=request.user,
            latitude=latitude,
            longitude=longitude,
            start_time=now,
            end_time=now
        )
    
    return JsonResponse({
        'status': 'success',
        'latitude': location_entry.latitude,
        'longitude': location_entry.longitude,
        'recorded_at': location_entry.recorded_at.isoformat()
    })

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