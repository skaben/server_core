from django.contrib import admin

from django.contrib.auth.models import Group, User

from core.models.mqtt import DeviceTopic, ControlReaction
from core.models.system import SystemSettings
from events.models import EventRecord


class BaseSiteAdmin(admin.AdminSite):

    site_title = 'SKABEN'
    site_header = 'Dungeon admin'
    index_title = 'Управление системами'


base_site = BaseSiteAdmin()
base_site.register(User)
base_site.register(Group)


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
admin.site.register(EventRecord, site=base_site)
