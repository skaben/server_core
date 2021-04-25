from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group, User


class BaseSiteAdmin(admin.AdminSite):

    site_title = 'SKABEN Dungeon'
    site_header = 'SKABEN Dungeon'
    index_title = 'Управление системами'


base_site = BaseSiteAdmin()
base_site.register(User)
base_site.register(Group)
