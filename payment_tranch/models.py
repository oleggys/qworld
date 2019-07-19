from django.db import models
# Create your models here.
from qworld.models import Quest


class Promocode(models.Model):
    class Meta:
        verbose_name_plural = 'Скидочные купоны'

    code = models.CharField('Код', max_length=12)
    discount = models.IntegerField('Скидка в %', default=0)

    def __str__(self):
        return self.code


class Order(models.Model):
    uuid = models.CharField('ID заказа', max_length=64,
                            default='', primary_key=True)
    count = models.PositiveIntegerField('Кол-во', default=1)
    amount = models.PositiveIntegerField('Сумма заказа')
    quest_id = models.IntegerField('id квеста')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.uuid


class Part_Order(models.Model):
    uuid = models.CharField('ID заказа', max_length=64,
                            default='', primary_key=True)
    count = models.PositiveIntegerField('Кол-во', default=1)
    amount = models.PositiveIntegerField('Сумма заказа', default=0)
    quest_id = models.IntegerField('id квеста')
    user_id = models.PositiveIntegerField('id пользователя')

    class Meta:
        verbose_name = 'Заказ участия'
        verbose_name_plural = 'Заказы на участие в квестах'

    def __str__(self):
        return self.uuid


class Application(models.Model):
    user_id = models.IntegerField('id пользователя')
    amount = models.IntegerField('Сумма выплаты')
    purse = models.CharField('Яндекс кошелёк', max_length=30)

    class Meta:
        verbose_name = 'Заявка на выплату'
        verbose_name_plural = 'Заявки на выплату'