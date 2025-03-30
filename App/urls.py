"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from . import views

app_name = 'App'

urlpatterns = [
    path("", views.index, name='index'),
    path('update-location/', views.update_location, name='update_location'),
    path("finalize-location/", views.finalize_location, name="finalize_location"),
    path("login/", views.login, name='login'),
    path("logout/", views.logout_view, name='logout'),
    path("help/", views.help, name='help'),
    path("profile/", views.profile, name='profile'),
    path("home/", views.home, name='home'),
    path("accounts/", include("allauth.urls")),
    path('diagnose/', views.diagnose, name='diagnose'),
    path('report_physical_illness/', views.report_physical_illness, name='report_physical_illness'),
    path('report_airborne_illness/', views.report_airborne_illness, name='report_airborne_illness'),
    path("archive/", views.archive, name='archive'),
    path("learn/", views.learn, name='learn'),
    path("view_notification/", views.view_notification, name ='view_notification'),
    path("archive_notification/", views.archive_notification, name ='archive_notification'),
    path("admin_visualization/", views.admin_visualization_view, name='admin_visualization_view')
]
