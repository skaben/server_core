from django.contrib import admin

from core.admin import base_site

from peripheral_devices.models import (
    LockDevice,
    TerminalDevice,
)
from peripheral_behavior.models import (
    PassiveConfig,
)


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp', 'alert_state')


admin.site.register(LockDevice, DeviceAdmin, site=base_site)
admin.site.register(TerminalDevice, DeviceAdmin, site=base_site)
# регистрируется как девайс, т.к. нет отдельного поведения
admin.site.register(PassiveConfig, admin.ModelAdmin, site=base_site)
