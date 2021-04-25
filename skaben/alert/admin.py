from django.contrib import admin

from .models import AlertCounter, AlertState

admin.site.register(AlertCounter)
admin.site.register(AlertState)
