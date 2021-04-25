from django.contrib import admin

from skaben.admin import base_site

from .models import AlertCounter, AlertState

admin.site.register(AlertCounter, site=base_site)
admin.site.register(AlertState, site=base_site)
