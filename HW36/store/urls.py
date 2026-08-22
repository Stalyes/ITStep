from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    path("sale/", views.sale_products, name="sale_products"),
]
