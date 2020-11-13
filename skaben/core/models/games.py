from django.db import models


class HackGame(models.Model):

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
        verbose_name = 'Настройки мини-игры взлома'
        verbose_name_plural = 'Настройки мини-игр взлома'

    attempts = models.IntegerField(default=3)
    difficulty = models.IntegerField(choices=difficulty_choices,
                                     default=normal)
    wordcount = models.IntegerField(default=15)
    chance = models.IntegerField(default=15)


class AnotherGame(models.Model):
    class Meta:
        verbose_name = 'Настройки мини-игры'
        verbose_name_plural = 'Настройки мини-игр'

    attempts = models.IntegerField(default=3)
    wordcount = models.IntegerField(default=15)
    chance = models.IntegerField(default=10)

