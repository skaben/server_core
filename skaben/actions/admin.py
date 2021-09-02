from django.contrib import admin
from skaben.admin import base_site

from .models import EnergyState


#class EnergyStateAdmin(admin.ModelAdmin):

admin.site.register(EnergyState, site=base_site)