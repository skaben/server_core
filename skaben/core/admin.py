from django.contrib import admin
from core import models


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ("has_files",)


class DeviceAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)


# Register your models here.

admin.site.register(models.AccessCode)
admin.site.register(models.AlertCounter)
admin.site.register(models.AlertState)
admin.site.register(models.TextFile)
admin.site.register(models.HackGame)
admin.site.register(models.EventLog)
admin.site.register(models.Lock, DeviceAdmin)
admin.site.register(models.MenuItem)
admin.site.register(models.Permission)
# admin.site.register(models.SimpleLight)
admin.site.register(models.Terminal, DeviceAdmin)
admin.site.register(models.WorkMode, WorkModeAdmin)
admin.site.register(models.AudioFile)
admin.site.register(models.VideoFile)
admin.site.register(models.ImageFile)
admin.site.register(models.UserInput)
