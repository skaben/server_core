from django.contrib import admin
from core import models


class WorkModeAdmin(admin.ModelAdmin):
    readonly_fields = ["get_assoc_files", ]


# Register your models here.

admin.site.register(models.AccessCode)
admin.site.register(models.AlertCounter)
admin.site.register(models.AlertState)
#admin.site.register(models.ConfigString)
admin.site.register(models.TextDocument)
admin.site.register(models.HackGame)
admin.site.register(models.EventLog)
admin.site.register(models.Lock)
admin.site.register(models.MenuItem)
admin.site.register(models.Permission)
admin.site.register(models.SimpleLight)
admin.site.register(models.Terminal)
admin.site.register(models.WorkMode, WorkModeAdmin)
admin.site.register(models.AudioFile)
admin.site.register(models.VideoFile)
admin.site.register(models.ImageFile)
