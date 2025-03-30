from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import json
import math
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import LocationHistory, RelevantLocation
import django.utils.timezone as timezone
from .forms import PhysicalReportForm


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


@csrf_exempt  # For demonstration only; handle CSRF properly in production.
@require_POST
@login_required
def update_location(request):
    try:
        data = json.loads(request.body)
        latitude = data['latitude']
        longitude = data['longitude']
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    
    # Always record the location history.
    location_entry = LocationHistory.objects.create(
        user=request.user,
        latitude=latitude,
        longitude=longitude
    )
    
    now = timezone.now()
    RADIUS_THRESHOLD = 50  # meters
    # We use a short time threshold here for updating the pending entry.
    # (The final validation later will use 30 minutes as the required minimum.)
    PENDING_TIMEOUT = 5 * 60  # 5 minutes (for example)

    # Try to fetch the latest pending RelevantLocation entry (if any).
    pending = RelevantLocation.objects.filter(user=request.user).order_by('-end_time').first()

    if pending:
        # Compute the distance from the pending record’s reference point to the new location.
        distance = haversine(pending.latitude, pending.longitude, latitude, longitude)
        if distance <= RADIUS_THRESHOLD:
            # If within threshold, update the end_time.
            pending.end_time = now
            pending.save()
        else:
            # If the user moved outside the radius, finalize the pending record:
            duration = (pending.end_time - pending.start_time).total_seconds()
            if duration < 30 * 60:
                # If the duration is insufficient (under 30 minutes), delete the pending record.
                pending.delete()
            # Start a new pending RelevantLocation record.
            RelevantLocation.objects.create(
                user=request.user,
                latitude=latitude,
                longitude=longitude,
                start_time=now,
                end_time=now
            )
    else:
        # No pending record exists; create one.
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

@csrf_exempt  # For demonstration only; handle CSRF properly in production.
@require_POST
@login_required
def finalize_location(request):
    now = timezone.now()
    TIME_THRESHOLD = 30 * 60  # 30 minutes in seconds

    pending = RelevantLocation.objects.filter(user=request.user).order_by('-end_time').first()
    if pending:
        duration = (pending.end_time - pending.start_time).total_seconds()
        if duration < TIME_THRESHOLD:
            pending.delete()
            return JsonResponse({'status': 'deleted', 'message': 'Relevant location deleted due to insufficient duration'})
        else:
            # Optionally, mark it as finalized or do nothing.
            return JsonResponse({'status': 'kept', 'message': 'Relevant location retained'})
    return JsonResponse({'status': 'none', 'message': 'No pending relevant location found'})

def index(request):
    if request.user.is_authenticated:
        notifications = None #update once we have data structure in models
        return render(request, "index.html", {'Notifications':notifications})
    else: return render(request, "login.html")

def report_illness(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = PhysicalReportForm(request.POST)
            if form.is_valid():
                form.save()  # Save the data to the database
                return redirect('index')  # Redirect to a success page or another view
        else:
            form = PhysicalReportForm()
        
        return render(request, 'report.html', {'form': form})
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