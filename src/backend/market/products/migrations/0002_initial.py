# Generated by Django 4.2.11 on 2024-03-26 12:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='owner',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shop', to=settings.AUTH_USER_MODEL, verbose_name='Shop owner'),
        ),
        migrations.AddField(
            model_name='productparameter',
            name='parameter',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='products.parameter', verbose_name='Параметр'),
        ),
        migrations.AddField(
            model_name='productparameter',
            name='product_info',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_parameters', to='products.productinfo', verbose_name='Информация о продукте'),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='parameters',
            field=models.ManyToManyField(blank=True, through='products.ProductParameter', to='products.parameter', verbose_name='Параметры товара'),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='product',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='products.product', verbose_name='Product'),
        ),
        migrations.AddField(
            model_name='productinfo',
            name='shop',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='products.shop', verbose_name='Shop'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='products', to='products.category', verbose_name='Category'),
        ),
        migrations.AddField(
            model_name='category',
            name='shops',
            field=models.ManyToManyField(blank=True, related_name='categories', to='products.shop', verbose_name='Shops'),
        ),
        migrations.AddConstraint(
            model_name='productparameter',
            constraint=models.UniqueConstraint(fields=('product_info', 'parameter'), name='unique_product_parameter'),
        ),
        migrations.AddConstraint(
            model_name='productinfo',
            constraint=models.UniqueConstraint(fields=('product', 'shop', 'code_id'), name='unique_product_info'),
        ),
    ]
