from django.contrib import admin
from django.urls import path

from django.contrib.auth.models import Group, User

from core.models.mqtt import DeviceTopic, ControlReaction
from core.models.system import System
from events.models import EventRecord

from admin_extended.views import (
    upload_csv_view,
    download_example_csv,
)


class BaseSiteAdmin(admin.AdminSite):

    site_title = "SKABEN"
    site_header = "Dungeon admin"
    index_title = "Управление системами"


base_site = BaseSiteAdmin()
base_site.register(User)
base_site.register(Group)


class SystemAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("upload_csv/", self.admin_site.admin_view(upload_csv_view)),
            path("download_example_csv/", self.admin_site.admin_view(download_example_csv)),
        ]
        return my_urls + urls


class ControlCommandAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Основная настройка", {"fields": (("name", "channel"), "payload", "comment")}),
        ("Расширенная настройка роутинга", {"classes": ("collapse",), "fields": (("routing", "exchange"),)}),
    )


admin.site.register(ControlReaction, ControlCommandAdmin, site=base_site)
admin.site.register(System, SystemAdmin, site=base_site)
admin.site.register(DeviceTopic, SystemAdmin, site=base_site)
admin.site.register(EventRecord, site=base_site)
