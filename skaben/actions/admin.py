from django.contrib import admin

from skaben.admin import base_site

from .models import Action, UserInput

admin.site.register(Action, site=base_site)
admin.site.register(UserInput, site=base_site)

