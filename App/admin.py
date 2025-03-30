from django.contrib import admin

# Register your models here.
from .models import Disease, Infection, LocationHistory, RelevantLocation, PhysicalReport, AirborneReport

admin.site.register(Disease)
admin.site.register(Infection)
admin.site.register(LocationHistory)
admin.site.register(RelevantLocation)
admin.site.register(PhysicalReport)
admin.site.register(AirborneReport)
