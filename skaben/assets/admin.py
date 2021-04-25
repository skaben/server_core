from django.contrib import admin


class FileAdmin(admin.ModelAdmin):
    exclude = ('hash',)