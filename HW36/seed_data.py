import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "catalog.settings")
django.setup()

from store.models import Category, Product

Product.objects.all().delete()
Category.objects.all().delete()

category_data = [
    ("Desk Setup", "desk-setup"),
    ("Daily Carry", "daily-carry"),
    ("Home Comfort", "home-comfort"),
    ("Audio", "audio"),
]
categories = {
    slug: Category.objects.create(name=name, slug=slug)
    for name, slug in category_data
}

products = [
    ("Alto Desk Lamp", "Warm light with a focused, adjustable neck.", "desk-setup", 84.00, True, 15),
    ("Fold Cable Tray", "A clean landing place for every charging cable.", "desk-setup", 32.00, False, 0),
    ("Field Notebook Set", "Three durable notebooks for plans, lists, and sketches.", "daily-carry", 18.00, True, 20),
    ("Canvas Utility Tote", "A roomy everyday carry made from sturdy canvas.", "daily-carry", 46.00, False, 0),
    ("Cloud Throw", "A soft woven layer for slow evenings at home.", "home-comfort", 72.00, True, 10),
    ("Stoneware Mug", "Hand-finished ceramic with a comfortable wide handle.", "home-comfort", 24.00, False, 0),
    ("Mono Wireless Speaker", "Compact room-filling sound with a calm, tactile dial.", "audio", 129.00, True, 12),
    ("Pocket Headphones", "Lightweight headphones for focused listening anywhere.", "audio", 64.00, False, 0),
    ("Archive Radio", "A small analog-inspired radio for kitchen counters.", "audio", 98.00, False, 0),
]
Product.objects.bulk_create(
    [
        Product(
            category=categories[slug],
            name=name,
            description=description,
            price=price,
            available=True,
            has_discount=has_discount,
            discount_percent=discount_percent,
        )
        for name, description, slug, price, has_discount, discount_percent in products
    ]
)
print(f"Loaded {Category.objects.count()} categories and {Product.objects.count()} products.")
