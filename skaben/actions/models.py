import logging
from typing import Optional

import requests
from alert.models import AlertState
from django.db import models
from django.conf import settings


def get_default_dict():
    return {}


class Action(models.Model):

    ENDPOINT_CHOICES = (
        ('change_state', f'{settings.API_URL}/alert_state/set_current_by_name')  # existing {'name': 'state_name'}
    )

    endpoint = models.URLField()
    payload = models.JSONField(default=get_default_dict, blank=True, null=True)
    comment = models.TextField(default='')

    def execute(self):
        """Execute Action"""
        payload = self.payload or {}
        return requests.post(str(self.endpoint), data=payload)

    def __str__(self):
        return f'Action {self.endpoint}'


class UserInput(models.Model):

    class Meta:
        verbose_name = 'Обратная связь - команда'
        verbose_name_plural = 'Обратная связь - команды'

    name = models.CharField(default="inputname",
                            blank=False,
                            unique=True,
                            max_length=48)
    require = models.CharField(default="input", max_length=48)
    actions = models.ManyToManyField(Action)

    def __str__(self):
        return f"on input `{self.require}` put internal `{self.actions}`"
