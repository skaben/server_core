from core import models
from django.contrib import admin


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)

class SimpleConfigAdmin(admin.ModelAdmin):
    readonly_fields = ('config',)

class FileAdmin(admin.ModelAdmin):
    exclude = ('hash',)

# Register your models here.

admin.site.register(models.AccessCode)
admin.site.register(models.AlertCounter)
admin.site.register(models.AlertState)
admin.site.register(models.HackGame)
admin.site.register(models.EventLog)
admin.site.register(models.Lock, DeviceAdmin)
admin.site.register(models.MenuItem)
admin.site.register(models.Permission)
admin.site.register(models.Simple)
admin.site.register(models.SimpleConfig)
admin.site.register(models.Terminal, DeviceAdmin)
admin.site.register(models.WorkMode, WorkModeAdmin)
admin.site.register(models.TextFile)
admin.site.register(models.AudioFile, FileAdmin)
admin.site.register(models.VideoFile, FileAdmin)
admin.site.register(models.ImageFile, FileAdmin)
admin.site.register(models.UserInput, FileAdmin)
