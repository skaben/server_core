from django.contrib import admin
from core import models

# Register your models here.

admin.site.register(models.AccessCode)
admin.site.register(models.AlertCounter)
admin.site.register(models.AlertState)
admin.site.register(models.ConfigString)
admin.site.register(models.Document)
admin.site.register(models.EventLog)
admin.site.register(models.Lock)
admin.site.register(models.MenuItem)
admin.site.register(models.Permission)
admin.site.register(models.Tamed)
admin.site.register(models.Terminal)
