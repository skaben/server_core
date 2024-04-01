from django.contrib import admin
from core.admin import base_site
from alert.models import AlertCounter, AlertState


class AlertStateCustomAdmin(admin.ModelAdmin):
    """Админка статусов тревоги."""

    list_display = ('current', 'name', 'info', 'order', 'threshold', 'modifier')

    list_filter = [
        'current',
    ]

    fieldsets = (
        ('Параметры уровня тревоги', {
            'classes': ('none',),
            'fields': (
                ('name', 'current'),
                ('info', 'order'),
                'modifier',
                'threshold',
            )
        }),
    )

class AlertCounterCustomAdmin(admin.ModelAdmin):
    """Админка счетчиков тревоги."""

    list_display = ('timestamp', 'value', 'comment')
    readonly_fields = ('timestamp',)


admin.site.register(AlertCounter, AlertCounterCustomAdmin, site=base_site)
admin.site.register(AlertState, AlertStateCustomAdmin, site=base_site)
