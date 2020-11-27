from django.db import models


class HackGame(models.Model):

    """Fallout-style hacking game

       difficulty choices is a length of words
    """

    easy = 6
    normal = 8
    medium = 10
    hard = 12

    difficulty_choices = (
        (easy, 'easy'),
        (normal, 'normal'),
        (medium, 'medium'),
        (hard, 'hard'),
    )

    class Meta:
        verbose_name = 'Настройки: (Терминал) мини-игры Fallout Hack'
        verbose_name_plural = 'Настройки: (Терминал) мини-игра Fallout Hack'

    attempts = models.IntegerField(default=3)
    difficulty = models.IntegerField(choices=difficulty_choices,
                                     default=normal)
    wordcount = models.IntegerField(default=15)
    chance = models.IntegerField(default=15)


class AnotherGame(models.Model):
    class Meta:
        verbose_name = 'Настройки: (Терминал) мини-игры'
        verbose_name_plural = 'Настройки: (Терминал) мини-игр'

    attempts = models.IntegerField(default=3)
    wordcount = models.IntegerField(default=15)
    chance = models.IntegerField(default=10)

