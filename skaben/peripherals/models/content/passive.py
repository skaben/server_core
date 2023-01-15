from django.db import models

__all__ = 'PassiveConfig'


class PassiveConfig(models.Model):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
    """

    class Meta:
        verbose_name = 'Поведение пассивного устройства'
        verbose_name_plural = 'Поведение пассивных устройств'

    # fixme: get_default_dict
    config = models.JSONField(default=lambda: {})
    dev_type = models.CharField(max_length=16)
    state = models.ForeignKey('alert.AlertState',
                              on_delete=models.SET_NULL,
                              null=True,
                              blank=True)

    def __str__(self):
        name = 'UNDEFINED'
        if self.state:
            name = self.state.name.upper()
        return f'{self.dev_type} config [{name}] {self.config}'