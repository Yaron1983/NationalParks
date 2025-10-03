from django.contrib import admin
from .models import Park, Rating, ParkIdentifier
admin.site.register(Park)
admin.site.register(ParkIdentifier)
admin.site.register(Rating)
