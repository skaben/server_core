from django.contrib import admin

from core.admin import base_site

from peripheral_devices.models import (
    LockDevice,
    TerminalDevice,
    SimpleDevice
)


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp', 'alert')


admin.site.register(SimpleDevice, DeviceAdmin, site=base_site)
admin.site.register(LockDevice, DeviceAdmin, site=base_site)
admin.site.register(TerminalDevice, DeviceAdmin, site=base_site)
