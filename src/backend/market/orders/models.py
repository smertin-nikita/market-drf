from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import ProductInfo


class OrderStatus(models.TextChoices):
    """ Статус заказа """

    NEW = 'NEW', 'Новый'
    BASKET = 'BASKET', 'Корзина'
    CONFIRMED = 'CONFIRMED', 'Подтвержден'
    ASSEMBLED = 'ASSEMBLED', 'Собран'
    SENT = 'SENT', 'Отправлен'
    DELIVERED = 'DELIVERED',  'Доставлен'
    CANCELLED = 'CANCELLED', 'Отменен'


class Order(models.Model):
    """ Заказы. """

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказов"
        ordering = ('-created_at',)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        related_name='website',
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )

    status = models.TextField(
        choices=OrderStatus.choices,
        verbose_name='Статус',
        default=OrderStatus.BASKET
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    amount = models.DecimalField(
        null=False,
        blank=True,
        default=0,
        max_digits=12,
        decimal_places=2,
        verbose_name='Сумма',
    )

    products = models.ManyToManyField(
        ProductInfo, through='OrderItem',
        through_fields=["order", "product_info"],
        verbose_name='Позиции',
        blank=False
    )

    def __str__(self):
        return f'{self.status}, {self.amount} - {self.created_at}'


class OrderItem(models.Model):

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order', 'product_info'], name='unique_order_item'),
        ]

    order = models.ForeignKey(
        Order,
        verbose_name=_('Order'),
        related_name='order_items',
        blank=True,
        on_delete=models.CASCADE
    )

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name=_("Product's details"),
        related_name='order_items',
        blank=True,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"),
        default=1,
    )