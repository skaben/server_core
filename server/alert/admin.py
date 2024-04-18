from alert.models import AlertCounter, AlertState
from core.admin import base_site
from django.contrib import admin


class AlertStateCustomAdmin(admin.ModelAdmin):
    """Админка статусов тревоги."""

    list_display = (
        "current",
        "name",
        "info",
        "order",
        "threshold",
        "counter_increase",
        "counter_decrease",
    )

    list_filter = [
        "current",
    ]

    fieldsets = (
        (
            "Параметры уровня тревоги",
            {
                "classes": ("none",),
                "fields": (
                    ("name", "current"),
                    ("info", "order"),
                    "threshold",
                ),
            },
        ),
        (
            "Автоматическое изменение уровня",
            {
                "classes": ("none",),
                "fields": (
                    ("counter_increase", "auto_increase"),
                    ("counter_decrease", "auto_decrease"),
                ),
            },
        ),
    )


class AlertCounterCustomAdmin(admin.ModelAdmin):
    """Админка счетчиков тревоги."""

    list_display = ("timestamp", "value", "comment")
    readonly_fields = ("timestamp",)


admin.site.register(AlertCounter, AlertCounterCustomAdmin, site=base_site)
admin.site.register(AlertState, AlertStateCustomAdmin, site=base_site)
