import os
import random

from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("Set MONGO_URI before running this script.")

client = MongoClient(MONGO_URI)
collection = client["shop"]["products"]
collection.delete_many({})

categories = ["Electronics", "Books", "Clothes"]
products = []
for number in range(1, 51):
    quantity = random.randint(0, 100)
    products.append({
        "name": f"Product {number}",
        "category": random.choice(categories),
        "price": random.randint(50, 3000),
        "quantity": quantity,
        "available": quantity > 0,
    })

collection.insert_many(products)

print("--- All Products ---")
for product in collection.find():
    print(product)

print("\n--- Available Products ---")
for product in collection.find({"available": True}):
    print(product)

print("\n--- Products Above 1000 ---")
for product in collection.find({"price": {"$gt": 1000}}):
    print(product)

print("\n--- Product Count by Category ---")
category_counts = [{"$group": {"_id": "$category", "total_count": {"$sum": 1}}}]
for result in collection.aggregate(category_counts):
    print(f"{result['_id']}: {result['total_count']}")

collection.update_one(
    {"name": "Product 1"},
    {"$set": {"quantity": 25, "available": True}},
)
updated_product = collection.find_one({"name": "Product 1"})
print("\n--- Updated Product ---")
print(updated_product)
