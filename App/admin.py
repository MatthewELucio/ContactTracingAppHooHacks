from django.contrib import admin

# Register your models here.
from .models import Disease, Infection, LocationHistory, RelevantLocation

admin.site.register(Disease)
admin.site.register(Infection)
admin.site.register(LocationHistory)
admin.site.register(RelevantLocation)


