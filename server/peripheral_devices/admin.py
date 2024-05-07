from core.admin import base_site
from django.contrib import admin
from peripheral_behavior.models import PassiveConfig, Permission
from peripheral_devices.models import LockDevice, TerminalDevice


class PermissionInline(admin.TabularInline):
    model = Permission
    extra = 1


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ("timestamp", "alert", "online")
    list_display = (
        "description",
        "online",
        "ip",
        "mac_addr",
    )

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
    inlines = [PermissionInline]
    list_display = DeviceAdmin.list_display + ("closed", "blocked", "sound")
    list_filter = DeviceAdmin.list_filter + ("closed", "blocked", "sound")
    list_editable = DeviceAdmin.list_editable + ("closed", "blocked", "sound")
    fieldsets = DeviceAdmin.fieldsets + (
        (
            "Настройки замка",
            {
                "classes": ("none",),
                "fields": ("closed", "blocked", "sound", "timer"),
            },
        ),
    )


admin.site.register(LockDevice, LockAdmin, site=base_site)
admin.site.register(TerminalDevice, DeviceAdmin, site=base_site)
# регистрируется как девайс, т.к. нет отдельного поведения
admin.site.register(PassiveConfig, admin.ModelAdmin, site=base_site)
