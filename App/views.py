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
from .forms import PhysicalReportForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PhysicalReportForm, PersonForm, PersonFormSet
from .models import ReportPerson


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

# def report_illness(request):
#     if request.user.is_authenticated:
#         if request.method == 'POST':
#             form = PhysicalReportForm(request.POST)
#             if form.is_valid():
#                 form.save()  # Save the data to the database
#                 return redirect('index')  # Redirect to a success page or another view
#         else:
#             type = request.GET.get('type', 'physical')
#             if type == 'physical':
#                 form = PhysicalReportForm()
#             elif type == 'airborne':
#                 #form = AirborneReportFrom()
#                 form = PhysicalReportForm()
#             else:
#                 return render(request, 'index.html', {'error': 'form'})
        
#         return render(request, 'report.html', {'form': form})
#     else: return render(request, "login.html")

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PhysicalReportForm, PersonForm, PersonFormSet
from .models import ReportPerson
from django.forms import formset_factory


@login_required
def report_illness(request):
    # Create the formset class for Person forms
    PersonFormSet = formset_factory(PersonForm, extra=1)
    
    if request.method == 'POST':
        report_form = PhysicalReportForm(request.POST)
        person_formset = PersonFormSet(request.POST, prefix='persons')
        
        if report_form.is_valid() and person_formset.is_valid():
            # Save the report (assign the current user)
            physical_report = report_form.save(commit=False)
            physical_report.user = request.user
            physical_report.save()
            
            # Process each form in the formset
            for form in person_formset:
                # Check if the form has data (skip empty forms)
                if form.cleaned_data and (form.cleaned_data.get('first_name') or form.cleaned_data.get('last_name')):
                    ReportPerson.objects.create(
                        report=physical_report,
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )
            return redirect('index')  # or a success page
    else:
        report_form = PhysicalReportForm()
        person_formset = PersonFormSet(prefix='persons')
    
    return render(request, 'report.html', {
        'report_form': report_form,
        'person_formset': person_formset,
    })


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