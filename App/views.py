from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import json
import math
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import LocationHistory, RelevantLocation, Disease
import django.utils.timezone as timezone
from .forms import PhysicalReportForm, ProfileForm
import requests
from django.conf import settings
from django.views.decorators.http import require_GET



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


@csrf_exempt  # For demonstration only; ensure proper CSRF handling in production.
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
    TIME_THRESHOLD = 20 * 60  # 30 minutes in seconds
    window_start = now - timedelta(seconds=TIME_THRESHOLD)
    RADIUS_THRESHOLD = 50  # in meters

    # Retrieve all location entries in the last 30 minutes.
    recent_entries = LocationHistory.objects.filter(
        user=request.user,
        recorded_at__gte=window_start
    ).order_by('recorded_at')

    if recent_entries.exists():
        # Use the first entry as the reference point.
        ref = recent_entries.first()
        all_within_radius = True
        for entry in recent_entries:
            distance = haversine(ref.latitude, ref.longitude, entry.latitude, entry.longitude)
            if distance > RADIUS_THRESHOLD:
                all_within_radius = False
                break

        if all_within_radius:
            # The user has been within the radius for at least 30 minutes.
            # Check if a RelevantLocation record already exists for this period.
            relevant = RelevantLocation.objects.filter(
                user=request.user,
                start_time__gte=window_start
            ).order_by('start_time').first()
            if relevant:
                # Update its end_time to now.
                relevant.end_time = now
                relevant.save()
            else:
                # Create a new RelevantLocation record.
                RelevantLocation.objects.create(
                    user=request.user,
                    latitude=ref.latitude,
                    longitude=ref.longitude,
                    start_time=recent_entries.first().recorded_at,
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
            type = request.GET.get('type', 'physical')
            if type == 'physical':
                form = PhysicalReportForm()
            elif type == 'airborne':
                #form = AirborneReportFrom()
                form = PhysicalReportForm()
            else:
                return render(request, 'index.html', {'error': 'form'})
        
        return render(request, 'report.html', {'form': form})
    else: return render(request, "login.html")

def learn(request):
    if request.user.is_authenticated:
        diseases = Disease.objects.all()
        return render(request, "learn.html", {'Diseases': diseases})
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
    user = request.user  # Get the current user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # Save the updated user data
            return render(request, 'profile.html', {'msg': 'complete'})  # Redirect to the same page after successful save
    else:
        form = ProfileForm(instance=user)

    return render(request, 'profile.html', {'form': form})

@login_required
def home(request):
    if request.user.is_authenticated:
        return render(request, "home.html", {'email': request.user.email}) 
    else: return render(request, "login.html")


def condition_search(request):
    """
    This view queries the external Medical Conditions API and renders the learn.html page.
    The learn.html template should include the condition search card that uses the provided
    context variables (query, results, error) to display search results.
    """
    query = request.GET.get('q', '')  # Get the search term from the query string
    results = None
    error = None

    if query:
        base_url = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"
        params = {
            'terms': query,                     # The search term(s)
            'maxList': 7,                       # Limit number of returned results (default is 7)
            'df': 'term_icd9_code,primary_name', # Fields to display
            # Other parameters can be added here as needed:
            # 'sf': 'consumer_name,primary_name,...',
            # 'ef': 'term_icd9_code,term_icd9_text',
            # 'offset': 0, etc.
        }
        try:
            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()  # Raise an exception for HTTP errors
            results = response.json()
        except requests.RequestException as e:
            error = str(e)
    
    context = {
        'query': query,
        'results': results,
        'error': error,
    }
    # Render the learn.html template so that the condition search appears in the right column.
    return render(request, 'learn.html', context)

@require_GET
def condition_autocomplete(request):
    """
    This view returns a JSON response containing a list of primary names for medical conditions,
    which can be used for an autocomplete feature on the frontend.
    """
    query = request.GET.get('q', '')
    data = {}
    if query:
        base_url = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"
        params = {
            'terms': query,
            'maxList': 7,
            'df': 'primary_name',
        }
        try:
            response = requests.get(base_url, params=params, timeout=5)
            response.raise_for_status()
            results = response.json()
            # Extract the primary names from the display array (located at index 3).
            display_results = [item[0] for item in results[3]] if results and len(results) >= 4 else []
            data = {'results': display_results}
        except Exception as e:
            data = {'error': str(e)}
    return JsonResponse(data)