import random
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://tornikeodo_db_user:K4U58btMUGN3lE2P@strongcluster.toj2pmh.mongodb.net/?appName=strongcluster"

client = MongoClient(MONGO_URI)
db = client["shop"]
collection = db["products"]

collection.delete_many({})

categories = ["Electronics", "Books", "Clothes"]
products_list = []

for i in range(1, 51):
    quantity = random.randint(0, 100)
    product = {
        "name": f"Product {i}",
        "category": random.choice(categories),
        "price": random.randint(50, 3000),
        "quantity": quantity,
        "available": quantity > 0,
    }
    products_list.append(product)

collection.insert_many(products_list)

print("--- All Products ---")
for item in collection.find():
    print(
        f"{item['name']} | Category: {item['category']} | Price: {item['price']} | Quantity: {item['quantity']} | Available: {item['available']}"
    )

print("\n--- Available Products Only ---")
for item in collection.find({"available": True}):
    print(
        f"{item['name']} | Quantity: {item['quantity']} | Price: {item['price']}"
    )

print("\n--- Products with Price > 1000 ---")
for item in collection.find({"price": {"$gt": 1000}}):
    print(
        f"{item['name']} | Price: {item['price']} | Category: {item['category']}"
    )

print("\n--- Product Count by Category ---")
pipeline = [{"$group": {"_id": "$category", "total_count": {"$sum": 1}}}]

for stat in collection.aggregate(pipeline):
    print(f"Category: {stat['_id']} -> Total: {stat['total_count']}")

print("\n--- Update Product ---")
target_product = "Product 1"
new_qty = 25

collection.update_one(
    {"name": target_product},
    {"$set": {"quantity": new_qty, "available": new_qty > 0}},
)

updated_doc = collection.find_one({"name": target_product})
print(
    f"{updated_doc['name']} | New Quantity: {updated_doc['quantity']} | Available: {updated_doc['available']}"
)