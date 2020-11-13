from django.db import models
from .alert import AlertState


class ComplexConfig(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=128, default="config")
    state = models.ManyToManyField(AlertState, blank=False)

    def __str__(self):
        return f"{self.name} {self.id}"


class LockConfig(ComplexConfig):

    name = models.CharField(max_length=128, default="lock config")

    sound = models.BooleanField(default=False)
    closed = models.BooleanField(default=True)
    blocked = models.BooleanField(default=False)
    timer = models.IntegerField(default=10)


class TerminalConfig(ComplexConfig):

    name = models.CharField(max_length=128, default="terminal config")

    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    block_time = models.IntegerField(default=10)
    hacked = models.BooleanField(default=False)
