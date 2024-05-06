from core.admin import base_site
from django.contrib import admin
from peripheral_behavior.models import AccessCode, Permission, SkabenUser


class LockPermissionAdmin(admin.ModelAdmin):
    list_display = ("lock", "card", "state_id")


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


admin.site.register(SkabenUser, admin.ModelAdmin, site=base_site)
admin.site.register(AccessCode, admin.ModelAdmin, site=base_site)
admin.site.register(Permission, admin.ModelAdmin, site=base_site)
admin.site.register(Permission, LockPermissionAdmin, site=base_site)
