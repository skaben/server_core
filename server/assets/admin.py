from core.admin import base_site
from django.contrib import admin
from .models.input import UserInput
from .models.files import VideoFile, AudioFile, ImageFile, TextFile


class FileAdmin(admin.ModelAdmin):
    exclude = ("hash",)


class TextFileAdmin(admin.ModelAdmin):
    exclude = ("hash", "file")
    readonly_fields = ("uri",)


admin.site.register(AudioFile, FileAdmin, site=base_site)
admin.site.register(VideoFile, FileAdmin, site=base_site)
admin.site.register(ImageFile, FileAdmin, site=base_site)
admin.site.register(TextFile, TextFileAdmin, site=base_site)
admin.site.register(UserInput, admin.ModelAdmin, site=base_site)
