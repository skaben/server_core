import time
from django.db import models

# Create your models here.

#  DEVICES


class Dumb(models.Model):
    """
        Simple dumb device, such as lights, sirens, rgb-leds
        Controls only by predefined config JSON
    """

    class Meta:
        verbose_name = 'device: RGB (Dumb)'
        verbose_name_plural = 'devices: RGB (Dumbs)'

    ts = models.IntegerField(default=int(time.time()))
    descr = models.CharField(max_length=120, default='simple dumb')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    config = models.CharField(max_length=500) # config JSONable string

    def __str__(self):
        return f'DUMB ID: {self.id} {self.descr}'

class Terminal(models.Model):

    class Meta:
        verbose_name = 'device: Terminal'
        verbose_name_plural = 'devices: Terminals'

    ts = models.IntegerField(default=int(time.time()))
    descr = models.CharField(max_length=120, default='simple terminal')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    powered = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    hacked = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    lowered = models.BooleanField(default=False)
    hack_attempts = models.IntegerField(default=3)
    hack_length = models.IntegerField(default=4)
    hack_wordcount = models.IntegerField(default=15)
    menu_list = models.CharField(max_length=12)
    msg_header = models.CharField(max_length=100)
    msg_body = models.CharField(max_length=500)

    def __str__(self):
        return f'TERMINAL ID: {self.id} {self.descr}'

class Lock(models.Model):

    class Meta:
        verbose_name = 'device: Lock'
        verbose_name_plural = 'devices: Locks'

    ts = models.IntegerField(default=int(time.time()))
    descr = models.CharField(max_length=120, default='simple lock')
    online = models.BooleanField(default=False)
    ip = models.GenericIPAddressField()
    override = models.BooleanField(default=False)
    sound = models.BooleanField(default=False)
    opened = models.BooleanField(default=False)
    term_id = models.ForeignKey(Terminal,
                                null=True,
                                blank=True,
                                default=None,
                                on_delete=models.CASCADE)
    def __str__(self):
        return f'LOCK ID {self.id} {self.descr}'

#  COLORS AND PERMISSIONS


class State(models.Model):

    class Meta:
        verbose_name = 'Global Alert state'
        verbose_name_plural = 'Global Alert states'

    name = models.CharField(max_length=15) # alert level color name
    value = models.IntegerField()
    description = models.CharField(max_length=300)


class Card(models.Model):

    class Meta:
        verbose_name = 'Staff card'
        verbose_name_plural = 'Staff cards'

    long_id = models.CharField(max_length=16, default='a8a7a6a5a4a3a2a1')
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    department = models.CharField(max_length=30)
    position = models.CharField(max_length=30)


class Permission(models.Model):

    class Meta:
        verbose_name = 'Staff permission'
        verbose_name_plural = 'Staff permissions'

    card_id = models.ForeignKey(Card, on_delete=models.CASCADE)
    lock_id = models.ForeignKey(Lock, on_delete=models.CASCADE)
    state_id = models.ForeignKey(State, on_delete=models.CASCADE)



