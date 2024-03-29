# Generated by Django 4.2 on 2023-04-30 20:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alert", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alertstate",
            name="modifier",
            field=models.IntegerField(
                default=5,
                help_text="на сколько изменяется счетчик при ошибке прохождения данжа",
                verbose_name="штраф за ошибку",
            ),
        ),
        migrations.AlterField(
            model_name="alertstate",
            name="order",
            field=models.IntegerField(
                help_text="используется для идентификации и упорядочивания статуса без привязки к id в БД",
                unique=True,
                verbose_name="цифровой id статуса",
            ),
        ),
        migrations.AlterField(
            model_name="alertstate",
            name="threshold",
            field=models.IntegerField(
                default=-1,
                help_text="Нижнее значение счетчика счетчика тревоги для переключения в статус. Чтобы отключить авто-переключение - выставьте отрицательное значение",
                verbose_name="порог срабатывания ",
            ),
        ),
    ]
