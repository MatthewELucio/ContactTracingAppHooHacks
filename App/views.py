from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib.auth.models import Group
import math, datetime, json, folium, os
from folium.plugins import HeatMap
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import LocationHistory, RelevantLocation, Disease, NotificationV2
import django.utils.timezone as timezone
from .forms import PhysicalReportForm, AirborneReportForm, ProfileForm


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

def is_site_admin(user):
    return user.is_authenticated and user.groups.filter(name="site-admin").exists()

@user_passes_test(is_site_admin, login_url='/login')
def admin_visualization_view(request):
    user_locations = [
        ("admin", 38.0315141, -78.5106534, datetime(2025, 3, 29, 10, 0)),
        ("throwaway", 38.031536, -78.5105206, datetime(2025, 3, 29, 10, 30)),
        ("justin0", 38.0362287, -78.5071464, datetime(2025, 3, 29, 11, 0)),
    ]
    print("Generating exposure map...")  # Debugging step

    # Define the path to save the map in the static folder
    map_filename = "exposure_map.html"
    map_path = os.path.join(settings.BASE_DIR, 'static', map_filename)

    # Ensure the static folder exists, if not, create it

    # Generate and save the map
    generate_exposure_map(user_locations, save_path=map_path)

    return render(request, "admin_visualization.html", {"map_path": f"/static/{map_filename}"})

def generate_exposure_map(user_locations, radius=50, save_path=None):
    if not user_locations:
        print("No user locations provided.")
        return None
    
    print(f"Generating map for {len(user_locations)} locations...")

    # Determine the map center
    first_location = user_locations[0]
    map_center = (first_location[1], first_location[2])

    # Initialize the map
    exposure_map = folium.Map(location=map_center, zoom_start=15, control_scale=True)

    # Add circles for each location with infection radius
    for username, lat, lon, timestamp in user_locations:
        popup_text = f"{username} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"Adding circle for {username} at ({lat}, {lon})")

        folium.Circle(
            location=(lat, lon),
            radius=radius,  # Infection radius in meters
            color="red",
            fill=True,
            fill_color="red",
            fill_opacity=0.3,
            popup=popup_text
        ).add_to(exposure_map)

        # Add a marker at the center of each exposure zone
        folium.Marker(
            location=(lat, lon),
            popup=popup_text,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(exposure_map)

    # Add a heatmap layer for better visualization
    heatmap_data = [(lat, lon) for _, lat, lon, _ in user_locations]
    print(f"Adding heatmap with {len(heatmap_data)} data points.")

    HeatMap(heatmap_data, radius=30).add_to(exposure_map)

    # Save map to file if path is provided
    if save_path:
        print(f"Saving map to {save_path}")
        exposure_map.save(save_path)

    return exposure_map


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
        form = PhysicalReportForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'index.html', {'message': 'successful physical form'})
    else:
        form = PhysicalReportForm()

    return render(request, 'report_physical.html', {'form': form})

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
            # for person in potential_infected:
            #     NotificationV2.objects.create(
            #         user=person.user,  
            #         disease=report.illness, 
            #         message=f"Exposure alert: You may have been exposed to {report.illness}.",
            #     )

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