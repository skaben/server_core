from core.admin import base_site
from django.contrib import admin

from polymorphic.admin import PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from peripheral_behavior.models import (
    AccessCode,
    SkabenUser,
    TerminalAccount,
    LockBehavior,
    MenuItem,
    MenuItemImage,
    MenuItemVideo,
    MenuItemAudio,
    MenuItemText,
    MenuItemUserInput,
)


menu_inline_fields = ("label", "content", "timer")


class MenuItemAdmin(PolymorphicParentModelAdmin):
    verbose_name = "Пункт меню"
    verbose_name_plural = "Пункты меню"
    model = TerminalAccount.menu_items.through

    child_models = (
        MenuItemAudio,
        MenuItemVideo,
        MenuItemImage,
        MenuItemText,
        MenuItemUserInput,
    )


class PolymorphicChildInvisible(PolymorphicChildModelAdmin):
    def get_model_perms(self, request):
        return {"add": False, "change": False, "delete": False}


class MenuItemAudioAdmin(PolymorphicChildInvisible):
    model = MenuItemAudio
    fields = menu_inline_fields
    verbose_name = "Меню: аудио"


class MenuItemVideoAdmin(PolymorphicChildInvisible):
    model = MenuItemVideo
    fields = menu_inline_fields
    verbose_name = "Меню: видео"


class MenuItemImageAdmin(PolymorphicChildInvisible):
    model = MenuItemImage
    fields = menu_inline_fields
    verbose_name = "Меню: изображение"


class MenuItemTextAdmin(PolymorphicChildInvisible):
    model = MenuItemText
    fields = menu_inline_fields
    verbose_name = "Меню: текст"


class MenuItemUserInputAdmin(PolymorphicChildInvisible):
    model = MenuItemUserInput
    fields = ("label", "content", "input_label", "input_description", "timer")
    verbose_name = "Меню: пользовательский ввод"


class TerminalAccountAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    fields = (
        "user",
        "password",
        "header",
        "footer",
        "menu_items",
    )


admin.site.register(MenuItem, MenuItemAdmin, site=base_site)

# registering invisible polymorphic child admins
admin.site.register(MenuItemText, MenuItemTextAdmin)
admin.site.register(MenuItemAudio, MenuItemAudioAdmin)
admin.site.register(MenuItemVideo, MenuItemVideoAdmin)
admin.site.register(MenuItemImage, MenuItemImageAdmin)
admin.site.register(MenuItemUserInput, MenuItemUserInputAdmin)

admin.site.register(SkabenUser, admin.ModelAdmin, site=base_site)
admin.site.register(AccessCode, admin.ModelAdmin, site=base_site)
admin.site.register(TerminalAccount, TerminalAccountAdmin, site=base_site)
admin.site.register(LockBehavior, admin.ModelAdmin, site=base_site)
