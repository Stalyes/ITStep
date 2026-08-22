from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category_products", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    has_discount = models.BooleanField(default=False)
    discount_percent = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["price", "name"]

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        if self.has_discount and self.discount_percent:
            return self.price * (100 - self.discount_percent) / 100
        return self.price
