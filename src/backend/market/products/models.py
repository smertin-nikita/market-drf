from django.conf import settings
from django.contrib.postgres import validators
from django.db import models
from django.utils.translation import gettext_lazy as _


class Shop(models.Model):

    class Meta:
        verbose_name = _('Shop')
        verbose_name_plural = _("List of shops")
        ordering = ('-name',)

    name = models.CharField(max_length=50, verbose_name='Название', blank=True, default='')

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Shop owner'),
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='shop'
    )

    def __str__(self):
        return self.name


class Category(models.Model):

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _("List of categories")
        ordering = ('-name',)

    name = models.CharField(max_length=40, verbose_name=_('Name'), unique=True)

    shops = models.ManyToManyField(
        Shop,
        verbose_name=_("Shops"),
        related_name='categories',
        blank=True
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ('-name',)

    name = models.CharField(max_length=80, verbose_name=_("Name"))

    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):

    class Meta:
        verbose_name = _("Product's details")
        verbose_name_plural = _("List of product's details")
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'code_id'], name='unique_product_info'),
        ]

    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
    )

    shop = models.ForeignKey(
        Shop,
        verbose_name=_("Shop"),
        related_name='product_infos',
        blank=True,
        on_delete=models.CASCADE
    )

    code_id = models.PositiveIntegerField(verbose_name=_("Product's code"))

    model = models.CharField(
        max_length=80,
        verbose_name=_("Model"),
        blank=True
    )

    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"),
        default=1,
        validators=[validators.MinValueValidator(1), validators.MaxValueValidator(10000)]
    )

    price = models.DecimalField(
        verbose_name='Цена',
        null=False,
        blank=True,
        default=0,
        max_digits=12,
        decimal_places=2,
    )

    price_rrc = models.DecimalField(
        verbose_name='Рекомендуемая розничная цена',
        null=False,
        blank=True,
        default=0,
        max_digits=12,
        decimal_places=2,
    )

    parameters = models.ManyToManyField(
        'Parameter',
        verbose_name='Параметры товара',
        through='ProductParameter',
        blank=True

    )

    def __str__(self):
        return f'Товар {self.product.name} {self.model}'


class Parameter(models.Model):

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список имен параметров"
        ordering = ('-name',)

    name = models.CharField(max_length=40, verbose_name='Название')

    def __str__(self):
        return self.name


class ProductParameter(models.Model):

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    product_info = models.ForeignKey(
        ProductInfo,
        verbose_name='Информация о продукте',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )

    parameter = models.ForeignKey(
        Parameter, verbose_name='Параметр',
        related_name='product_parameters',
        blank=True,
        on_delete=models.CASCADE
    )

    value = models.CharField(verbose_name='Значение', max_length=100)