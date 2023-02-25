from django.contrib import admin

from core.admin import base_site

from peripheral_behavior.models import (
    SkabenUser,
    AccessCode,
    Permission,
)


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


# admin.site.register(MenuItem, site=base_site)
# admin.site.register(WorkMode, WorkModeAdmin, site=base_site)
admin.site.register(SkabenUser, site=base_site)
admin.site.register(AccessCode, site=base_site)
admin.site.register(Permission, site=base_site)
# admin.site.register(SimpleConfig, site=base_site)
