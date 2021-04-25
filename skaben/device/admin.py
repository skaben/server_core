from core import models
from django.contrib import admin


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)


class SimpleConfigAdmin(admin.ModelAdmin):
    readonly_fields = ('config',)
