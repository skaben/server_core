from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Terminal)
admin.site.register(Lock)
admin.site.register(Card)
admin.site.register(State)
admin.site.register(Permission)
admin.site.register(Dumb)

