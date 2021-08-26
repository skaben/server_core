from django.contrib import admin

from skaben.admin import base_site

from .models import DeviceChannel, ControlCommand


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


admin.site.register(DeviceChannel, site=base_site)
admin.site.register(ControlCommand, ControlCommandAdmin, site=base_site)
