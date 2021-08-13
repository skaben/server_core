import logging
from typing import Optional

import requests
from alert.models import AlertState
from django.db import models
from django.conf import settings


def get_default_dict():
    return {}

def _api(url: str) -> str:
    return f'{settings.API_URL}{url}'


CHANGE_STATE = 'change_state'


class Action(models.Model):

    ENDPOINT_CHOICES = (
        (_api("/alert_state/set_current_by_name"), CHANGE_STATE),
    )

    endpoint = models.URLField(choices=ENDPOINT_CHOICES, default=CHANGE_STATE)
    payload = models.JSONField(default=get_default_dict)
    comment = models.TextField(default='', blank=True)

    def execute(self):
        """Execute Action"""
        payload = self.payload or {}
        return requests.post(str(self.endpoint), data=payload)

    def __str__(self):
        return f'{self.get_endpoint_display()}'


class UserInput(models.Model):

    class Meta:
        verbose_name = 'Обратная связь - команда'
        verbose_name_plural = 'Обратная связь - команды'

    name = models.CharField(default="inputname",
                            blank=False,
                            unique=True,
                            max_length=48)
    require = models.CharField(default="required_input", max_length=64)
    message = models.TextField(default="required input")
    on_success = models.TextField(blank=True, null=True)
    on_fail = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Input `{self.name}` required `{self.require}`"
