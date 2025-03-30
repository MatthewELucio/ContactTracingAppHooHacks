from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.contrib.auth.models import Group
import math, random, datetime, json, folium, os
from folium.plugins import TimestampedGeoJson
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import LocationHistory, RelevantLocation, Disease, NotificationV2
import django.utils.timezone as timezone
from .forms import PhysicalReportForm2, AirborneReportForm2, ProfileForm
from allauth.socialaccount.models import SocialAccount
import requests
from django.conf import settings
from django.views.decorators.http import require_GET
from openai import OpenAI
from django.conf import settings
from django.views.decorators.http import require_http_methods
import os


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
    location_entries = LocationHistory.objects.all()
    user_locations = [
        (entry.user, entry.latitude, entry.longitude, entry.recorded_at) for entry in location_entries
    ]

    map_filename = "exposure_map.html"
    map_path = os.path.join(settings.BASE_DIR, 'static', map_filename)

    generate_exposure_map(user_locations, save_path=map_path)

    return render(request, "admin_visualization.html", {"map_path": f"/static/{map_filename}"})

def generate_exposure_map(user_locations, radius=50, save_path=None):
    if not user_locations:
        print("No user locations provided.")
        return None

    print(f"Generating map for {len(user_locations)} locations...")

    first_location = user_locations[0]
    map_center = (first_location[1], first_location[2])

    exposure_map = folium.Map(location=map_center, zoom_start=15, control_scale=True)

    colors = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]
    user_colors = {}

    features = []
    for username, lat, lon, timestamp in user_locations:
        if username not in user_colors:
            user_colors[username] = random.choice(colors)

        color = user_colors[username]
        # popup_text = f"{username} - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "time": timestamp.isoformat(),
                "style": {"color": color},
                "icon": "circle",
                # "popup": popup_text
            },
        }
        features.append(feature)

    TimestampedGeoJson(
        {"type": "FeatureCollection", "features": features},
        period="PT5M",
        add_last_point=True,
        auto_play=True,
        loop=True,
        max_speed=1,
        loop_button=True,
        date_options="YYYY-MM-DD HH:mm:ss",
        time_slider_drag_update=True,
    ).add_to(exposure_map)

    if save_path:
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

def archive_notification(request):
    if request.user.is_authenticated:
        notifications = NotificationV2.objects.filter(user=request.user).order_by('-created_at')
        print(f"User {request.user} has {notifications} notifications.")
        print(f"Notifications for {request.user.username}: {notifications.count()}")
        print(f'')
        return render(request, "index.html", {'Notifications':notifications})
    else: return render(request, "login.html")

def view_notification(request):
    if request.user.is_authenticated:
        notifications = None #update once we have data structure in models
        return render(request, "index.html", {'Notifications':notifications})
    else: return render(request, "login.html")

def index(request):
    if request.user.is_authenticated:
        notifications = NotificationV2.objects.filter(user=request.user).order_by('-created_at')
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
        print(f"Google accounts: {google_accounts}")
        
        names = []
        for first, last in zip(first_names, last_names):
            if first.strip() and last.strip():
                names.append({"first_name": first, "last_name": last})
                for account in google_accounts:
                    if account.user.first_name.lower() == first.strip().lower() and account.user.last_name.lower() == last.strip().lower():
                        # Perform the necessary action with the matched user
                        print(f"Matched user: {account.user.username}")
                        disease_instance = Disease.objects.filter(name=disease).first()
                        notif = NotificationV2.objects.create(
                            user=account.user,
                            disease=disease_instance,
                            message=f"You have been exposed to {disease}",
                            created_at=timezone.now()
                        )
                        notif.save()
                            
        form = PhysicalReportForm2(request.POST)
        if form.is_valid():
            form.save()
            return redirect('App:index')  # Redirect to the index page after saving the form
            return render(request, 'index.html', {'message': 'successful physical form'})
    else:
        form = PhysicalReportForm2()

    return render(request, 'report_physical.html', {'form': form})

def report_airborne_illness(request):
    if not request.user.is_authenticated:
        return render(request, "login.html")

    if request.method == 'POST':
        form = AirborneReportForm2(request.POST)
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
        form = AirborneReportForm2()

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
        notifications = NotificationV2.objects.filter(user=request.user).order_by('-created_at')
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


@require_http_methods(["GET", "POST"])
def diagnose(request):
    """
    Handles both GET (to render learn.html) and POST (to process the diagnosis form).
    On POST, it calls the ChatGPT API with the provided symptoms and returns the diagnosis
    in the context so that learn.html can display it in the diagnosis card.
    """
    context = {}

    # (Optional) If you need to pass along other data for learn.html, for example:
    # context['Diseases'] = Disease.objects.all()
    # context['query'] = request.GET.get('q', '')
    # context['results'] = ...  (if you want to keep condition search results)

    if request.method == "POST":
        diseases = Disease.objects.all()
        # Build a comma-separated string of valid disease names.
        valid_diseases = ", ".join([d.name for d in diseases])
        symptoms = request.POST.get("symptoms", "").strip()
        if not symptoms:
            context["error"] = "Please enter your symptoms."
            return render(request, "learn.html", context)

        # Build the prompt for ChatGPT.
        prompt = (
            f"Based on the following symptoms, provide the most likely diagnosis and any recommended next steps. "
            f"Only choose from the following valid diseases: {valid_diseases}. "
            "Please include a disclaimer that you are not a doctor and that this is not medical advice.\n\nSymptoms: "
            f"{symptoms}"
        )

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        try:
            response = client.chat.completions.create(model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that provides possible medical diagnoses based on symptoms. "
                        "When the user provides symptoms, analyze them and provide a response that only contains the most likely diagnosis."
                        "Do not add any disclaimers or additional information. "
                        "Responsd with 1 or 2 words that best describes the condition (e.g., 'flu', 'cold', 'COVID-19', etc."
                    )
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=150)
            diagnosis = response.choices[0].message.content.strip()
        except Exception as e:
            diagnosis = f"Error contacting the diagnosis service: {e}"

        # Add the symptoms and diagnosis to the context.
        context["symptoms"] = symptoms
        context["diagnosis"] = diagnosis
        context["Diseases"] = diseases  # Pass the list of diseases to the template for reference

    # Render learn.html with the current context.
    return render(request, "learn.html", context)
# def condition_search(request):
#     """
#     This view queries the external Medical Conditions API and renders the learn.html page.
#     The learn.html template should include the condition search card that uses the provided
#     context variables (query, results, error) to display search results.
#     """
#     query = request.GET.get('q', '')  # Get the search term from the query string
#     results = None
#     error = None

#     if query:
#         base_url = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"
#         params = {
#             'terms': query,                     # The search term(s)
#             'maxList': 7,                       # Limit number of returned results (default is 7)
#             'df': 'term_icd9_code,primary_name', # Fields to display
#             # Other parameters can be added here as needed:
#             # 'sf': 'consumer_name,primary_name,...',
#             # 'ef': 'term_icd9_code,term_icd9_text',
#             # 'offset': 0, etc.
#         }
#         try:
#             response = requests.get(base_url, params=params, timeout=5)
#             response.raise_for_status()  # Raise an exception for HTTP errors
#             results = response.json()
#         except requests.RequestException as e:
#             error = str(e)

#     context = {
#         'query': query,
#         'results': results,
#         'error': error,
#     }
#     # Render the learn.html template so that the condition search appears in the right column.
#     return render(request, 'learn.html', context)

# @require_GET
# def condition_autocomplete(request):
#     """
#     This view returns a JSON response containing a list of primary names for medical conditions,
#     which can be used for an autocomplete feature on the frontend.
#     """
#     query = request.GET.get('q', '')
#     data = {}
#     if query:
#         base_url = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search"
#         params = {
#             'terms': query,
#             'maxList': 7,
#             'df': 'primary_name',
#         }
#         try:
#             response = requests.get(base_url, params=params, timeout=5)
#             response.raise_for_status()
#             results = response.json()
#             # Extract the primary names from the display array (located at index 3).
#             display_results = [item[0] for item in results[3]] if results and len(results) >= 4 else []
#             data = {'results': display_results}
#         except Exception as e:
#             data = {'error': str(e)}
#     return JsonResponse(data)
