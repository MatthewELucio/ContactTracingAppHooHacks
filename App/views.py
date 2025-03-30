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
from .forms import PhysicalReportForm2, AirborneReportForm
from allauth.socialaccount.models import SocialAccount


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

def report_physical_illness(request):
    if not request.user.is_authenticated:
        return render(request, "login.html")

    if request.method == 'POST':
        disease = request.POST.get("disease")
        
        first_names = request.POST.getlist("first_name[]")
        last_names = request.POST.getlist("last_name[]")
        
        google_accounts = SocialAccount.objects.filter(provider='google')
        for account in google_accounts:
            print(account.user.first_name, account.user.last_name, account.user.email)
        
        names = []
        for first, last in zip(first_names, last_names):
            if first.strip() and last.strip():
                names.append({"first_name": first, "last_name": last})
                for account in google_accounts:
                    if account.user.first_name.lower() == first.strip().lower() and account.user.last_name.lower() == last.strip().lower():
                        # Perform the necessary action with the matched user
                        print(f"Matched user: {account.user.email}")
                            
        form = PhysicalReportForm2(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'index.html', {'message': 'successful physical form'})
    else:
        form = PhysicalReportForm2()

    return render(request, 'report_physical.html', {'form': form})

# def names_view(request):
#     if request.method == "POST":
#         # Retrieve lists of names from the request data
#         first_names = request.POST.getlist("first_name[]")
#         last_names = request.POST.getlist("last_name[]")
        
#         # Combine them into a list of dictionaries (or process as needed)
#         google_accounts = SocialAccount.objects.filter(provider='google')
#         print(google_accounts)
#         names = []
#         for first, last in zip(first_names, last_names):
#             if first.strip() or last.strip():
#                 names.append({"first_name": first, "last_name": last})
#                 for account in google_accounts:
#                     if account.user.first_name == first and account.user.last_name == last:
#                         # Perform the necessary action with the matched user
#                         print(f"Matched user: {account.user.email}")
        
#         # Debug or process further (e.g., save to a model)
#         print("Names received:", names)
#         return redirect("success")  # Or render a response

    # For GET requests, render the form template
    return render(request, "names_template.html")

def report_airborne_illness(request):
    if not request.user.is_authenticated:
        return render(request, "login.html")

    if request.method == 'POST':
        form = AirborneReportForm(request.POST)
        if form.is_valid():
            report = form.save()

            infection_start = report.symptoms_appeared_date
            infection_end = report.diagnosis_date if report.diagnosis_date else timezone.now()

            print(f"User {request.user.username} reported illness from {infection_start} to {infection_end}")

            radius_threshold = 50
            potential_infected = set()

            overlapping_locations = RelevantLocation.objects.filter(
                start_time__lt=infection_end,
                end_time__gt=infection_start
            ).exclude(user=request.user)

            print(f"Found {overlapping_locations.count()} overlapping location entries.")
            user_locations = RelevantLocation.objects.filter(
                user=request.user, start_time__lt=infection_end, end_time__gt=infection_start
            )

            for loc in user_locations:
                for entry in overlapping_locations:
                    distance = haversine(loc.latitude, loc.longitude, entry.latitude, entry.longitude)
                    print(f"Checking {entry.user.username} at ({entry.latitude}, {entry.longitude}) - Distance: {distance}m")

                    if distance <= radius_threshold:
                        potential_infected.add(entry.user)

            print(f"Potential infected users: {len(potential_infected)}")
            for user in potential_infected:
                print(f"Exposed user: {user.username}")

            return render(request, 'index.html', {'message': 'successful airborne form!'})

    else:
        form = AirborneReportForm()

    return render(request, "report_airborne.html", {"form": form})


def learn(request):
    if request.user.is_authenticated:
        diseases = Disease.objects.all()
        return render(request, "learn.html", {'Diseases': diseases})
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

def archive(request):
    if request.user.is_authenticated:
        notifications = None
        return render(request, "archive.html", {'Notifications': notifications}) 
    else: return render(request, "login.html")

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