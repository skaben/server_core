from django.contrib import admin

from skaben.admin import base_site

from .models import DeviceTopic, ControlReaction, SystemSettings
from eventlog.models import EventLog


class ControlCommandAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основная настройка', {
           'fields': (
               ('name', 'channel'),
               'payload',
               'comment'
           )
        }),
        ('Расширенная настройка роутинга', {
            'classes': ('collapse',),
            'fields': (
                ('routing', 'exchange'),
            )
        }),
    )


admin.site.register(DeviceTopic, site=base_site)
admin.site.register(ControlReaction, ControlCommandAdmin, site=base_site)
admin.site.register(SystemSettings, site=base_site)
admin.site.register(EventLog, site=base_site)
