from django.contrib import admin

from skaben.admin import base_site

from .models import EventLog

admin.site.register(EventLog, site=base_site)

