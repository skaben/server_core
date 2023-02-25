from django.contrib import admin
from core.admin import base_site
from assets.models import AudioFile, HackGame, ImageFile, TextFile, VideoFile, UserInput


class FileAdmin(admin.ModelAdmin):
    exclude = ('hash',)


class TextFileAdmin(admin.ModelAdmin):
    exclude = ('hash', 'file')
    readonly_fields = ('uri',)


admin.site.register(AudioFile, FileAdmin, site=base_site)
admin.site.register(VideoFile, FileAdmin, site=base_site)
admin.site.register(ImageFile, FileAdmin, site=base_site)
admin.site.register(UserInput, site=base_site)
admin.site.register(HackGame, site=base_site)
admin.site.register(TextFile, TextFileAdmin, site=base_site)
