from django.contrib import admin
from core.admin import base_site

from peripheral_behavior.models import (
    SkabenUser,
    AccessCode,
    Permission,
)


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


admin.site.register(SkabenUser, admin.ModelAdmin, site=base_site)
admin.site.register(AccessCode, admin.ModelAdmin, site=base_site)
admin.site.register(Permission, admin.ModelAdmin, site=base_site)
