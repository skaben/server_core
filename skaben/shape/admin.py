from django.contrib import admin

from skaben.admin import base_site

from .models import MenuItem, SimpleConfig, WorkMode


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


class SimpleConfigAdmin(admin.ModelAdmin):
    readonly_fields = ('config',)


admin.site.register(MenuItem, site=base_site)
admin.site.register(WorkMode, WorkModeAdmin, site=base_site)
admin.site.register(SimpleConfig, SimpleConfigAdmin, site=base_site)
