from django.contrib import admin

# Register your models here.
from .models import Disease, Infection, LocationHistory, RelevantLocation, PhysicalReport2, AirborneReport2, NotificationV2

admin.site.register(Disease)
admin.site.register(Infection)
admin.site.register(LocationHistory)
admin.site.register(RelevantLocation)
admin.site.register(PhysicalReport2)
admin.site.register(AirborneReport2)
admin.site.register(NotificationV2)