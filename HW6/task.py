def count_fruits():
    fruit_counts = {}
    while True:
        fruit = input("Enter your favorite fruit: ").strip().lower()
        if fruit == "stop":
            return fruit_counts
        if fruit:
            fruit_counts[fruit] = fruit_counts.get(fruit, 0) + 1


squares = {number: number ** 2 for number in range(1, 11)}
print(squares)

products = [
    {"cola": {"price": 1.5, "quantity": 10}},
    {"fanta": {"price": 2.5, "quantity": 5}},
    {"snickers": {"price": 3.5, "quantity": 12}},
    {"water": {"price": 4.5, "quantity": 8}},
    {"beer": {"price": 6.5, "quantity": 5}},
]

print("Product names:")
total_value = 0
for product in products:
    product_name, details = next(iter(product.items()))
    print(product_name)
    total_value += details["price"] * details["quantity"]

print(f"Total product value: {total_value:.2f}")
print(count_fruits())
