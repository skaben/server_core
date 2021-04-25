from django.contrib import admin


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


class SimpleConfigAdmin(admin.ModelAdmin):
    readonly_fields = ('config',)
