from alert.models import AlertCounter, AlertState
from core.admin import base_site
from django.contrib import admin


class AlertStateCustomAdmin(admin.ModelAdmin):
    """Админка статусов тревоги."""

    list_display = ("current", "name", "ingame", "info", "order", "threshold", "counter_increase", "counter_decrease")

    list_filter = ["current"]

    fieldsets = (
        (
            "Параметры уровня тревоги",
            {"classes": ("none",), "fields": (("name", "current"), ("info", "order"), "ingame", "threshold")},
        ),
        (
            "Реакции на действие игроков",
            {
                "classes": ("none",),
                "fields": ("counter_increase", "counter_decrease"),
            },
        ),
        (
            "Автоматическое изменение уровня",
            {
                "classes": ("none",),
                "fields": ("auto_change", "auto_level", "auto_timeout"),
            },
        ),
    )


class AlertCounterCustomAdmin(admin.ModelAdmin):
    """Админка счетчиков тревоги."""

    list_display = ("timestamp", "value", "comment")
    readonly_fields = ("timestamp",)


admin.site.register(AlertCounter, AlertCounterCustomAdmin, site=base_site)
admin.site.register(AlertState, AlertStateCustomAdmin, site=base_site)
