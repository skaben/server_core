from core.admin import base_site
from django.contrib import admin
from peripheral_behavior.models import PassiveConfig
from peripheral_devices.models import LockDevice, TerminalDevice


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "alert", "online")

    fieldsets = (
        (
            None,
            {
                "classes": ("none",),
                "fields": (("timestamp", "alert", "online"),),
            },
        ),
        (
            "Параметры устройства",
            {
                "classes": ("none",),
                "fields": ("ip", "mac_addr", "description"),
            },
        ),
        (
            "Отключить авто-обновление конфигурации",
            {
                "classes": ("none",),
                "fields": ("override",),
            },
        ),
    )


class LockAdmin(DeviceAdmin):
    fieldsets = DeviceAdmin.fieldsets + (
        (
            "Настройки доступа",
            {
                "classes": ("none",),
                "fields": ("permissions",),
            },
        ),
    )


admin.site.register(LockDevice, LockAdmin, site=base_site)
admin.site.register(TerminalDevice, DeviceAdmin, site=base_site)
# регистрируется как девайс, т.к. нет отдельного поведения
admin.site.register(PassiveConfig, admin.ModelAdmin, site=base_site)
