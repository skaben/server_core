from django.db import models
from core.models.base import BaseModelUUID
from peripheral_behavior.models import SkabenUser

__all__ = (
    'TerminalMenuItem',
    'TerminalAccount',
)


class TerminalMenuItem(BaseModelUUID):

    class Meta:
        verbose_name = 'Пункт меню терминала'
        verbose_name_plural = 'Пункты меню терминала'

    timer = models.SmallIntegerField(default=0)
    description = models.CharField(max_length=128)


class TerminalAccount(BaseModelUUID):
    """Terminal user account."""

    class Meta:
        verbose_name = 'Режим (полное меню) терминала'
        verbose_name_plural = 'Режим (полное меню) терминала'

    user = models.ForeignKey(SkabenUser, on_delete=models.CASCADE)
    header = models.CharField(max_length=64, default="terminal vt40k")
    footer = models.CharField(max_length=64, default="unauthorized access is strictly prohibited")
    menu_set = models.ManyToManyField('peripheral_behavior.TerminalMenuItem')

    @property
    def has_files(self):
        files = {}
        for item in self.menu_set.all():
            related = getattr(item, item.option)
            if hasattr(related, 'hash'):
                files.update({related.hash: related.uri})
        return files
