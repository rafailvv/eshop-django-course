import uuid

from django.contrib.auth.models import User
from django.db import models


class ProductManager(models.Manager):
    def in_stock(self):
        return self.get_queryset().filter(stock__gt=0)

    def get_sorted_by_price_desc(self):
        """Возвращает товары, отсортированные по цене от большего к меньшему."""
        return self.order_by("-price")

    def get_sorted_by_price_asc(self):
        """Возвращает товары, отсортированные по цене от меньшего к большему."""
        return self.order_by("price")





from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name="Описание")
    price = models.FloatField(verbose_name="Цена")
    stock = models.IntegerField(verbose_name="В наличии")
    attributes = models.ManyToManyField('Attribute', verbose_name="Свойства")
    image = models.ImageField(upload_to="products/", verbose_name="Изображение", blank=True, null=True)

    objects = ProductManager()

    def __str__(self):
        return f"{self.title}: #{self.id}"


    class Meta:
        db_table = 'product'
        indexes = [models.Index(fields=["price"])]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'



class ProductImage(models.Model):
    image = models.ImageField(upload_to="media", verbose_name="Изображение")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")

    class Meta:
        verbose_name = "Фото товара"
        verbose_name_plural = "Фото товаров"


class Attribute(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Свойство"
        verbose_name_plural = "Свойства"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
