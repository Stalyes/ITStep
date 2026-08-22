from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Category, Product


def category_list():
    return Category.objects.annotate(product_count=Count("products")).filter(product_count__gt=0)


def home(request):
    products = Product.objects.filter(available=True).select_related("category").order_by("price", "name")
    return render(request, "store/home.html", {"products": products, "categories": category_list()})


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(available=True).order_by("price", "name")
    return render(request, "store/category.html", {"category": category, "products": products, "categories": category_list()})


def sale_products(request):
    products = Product.objects.filter(available=True, has_discount=True).select_related("category").order_by("price", "name")
    return render(request, "store/sale.html", {"products": products, "categories": category_list()})
