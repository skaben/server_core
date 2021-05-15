from django.contrib import admin

from skaben.admin import base_site

from .models import Lock, Simple, Terminal


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp', 'alert')


admin.site.register(Simple, DeviceAdmin, site=base_site)
admin.site.register(Lock, DeviceAdmin, site=base_site)
admin.site.register(Terminal, DeviceAdmin, site=base_site)
