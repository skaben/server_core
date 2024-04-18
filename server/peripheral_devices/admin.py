from django import forms
from django.contrib import admin
import re

from core.admin import base_site

from peripheral_devices.models import (
    LockDevice,
    TerminalDevice,
)
from peripheral_behavior.models import (
    PassiveConfig,
)


class MacAddressFormField(forms.CharField):
    def to_python(self, value):
        cleaned_value = re.sub(r"[^a-zA-Z0-9]", "", value)
        return cleaned_value

    def prepare_value(self, value):
        if value:
            unformatted_mac = value.replace(":", "")
            return unformatted_mac
        return value


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "alert_state")
    mac_addr = MacAddressFormField(max_length=32)


admin.site.register(LockDevice, DeviceAdmin, site=base_site)
admin.site.register(TerminalDevice, DeviceAdmin, site=base_site)
# регистрируется как девайс, т.к. нет отдельного поведения
admin.site.register(PassiveConfig, admin.ModelAdmin, site=base_site)
