from core.admin import base_site
from django.contrib import admin
from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
from peripheral_behavior.models import (
    AccessCode,
    SkabenUser,
    TerminalAccount,
    MenuItem,
    MenuItemImage,
    MenuItemVideo,
    MenuItemAudio,
    MenuItemText,
    MenuItemUserInput,
)


menu_inline_fields = ("label", "content", "timer")


class MenuInline(StackedPolymorphicInline):
    verbose_name = "Пункт меню"
    verbose_name_plural = "Пункты меню"

    class MenuItemAudioInline(StackedPolymorphicInline.Child):
        model = MenuItemAudio
        fields = menu_inline_fields

    class MenuItemVideoInline(StackedPolymorphicInline.Child):
        model = MenuItemVideo
        fields = menu_inline_fields

    class MenuItemImageInline(StackedPolymorphicInline.Child):
        model = MenuItemImage
        fields = menu_inline_fields

    class MenuItemTextInline(StackedPolymorphicInline.Child):
        model = MenuItemText
        fields = menu_inline_fields

    class MenuItemUserInputInline(StackedPolymorphicInline.Child):
        model = MenuItemUserInput
        fields = ("label", "content", "input_label", "input_description", "timer")

    model = TerminalAccount.menu_items.through

    child_inlines = (
        MenuItemAudioInline,
        MenuItemVideoInline,
        MenuItemImageInline,
        MenuItemTextInline,
        MenuItemUserInputInline,
    )

    extra = 0


class TerminalAccountAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
    inlines = [MenuInline]
    fields = [field.name for field in TerminalAccount._meta.fields if field.name not in ("id", "uuid", "menu_items")]


admin.site.register(MenuItem, admin.ModelAdmin, site=base_site)
admin.site.register(SkabenUser, admin.ModelAdmin, site=base_site)
admin.site.register(AccessCode, admin.ModelAdmin, site=base_site)
admin.site.register(TerminalAccount, TerminalAccountAdmin, site=base_site)
