def camel_to_snake(name):
    return "".join(f"_{ch.lower()}" if ch.isupper() else ch for ch in name).lstrip("_")

text = input("შეიყვანეთ camelCase ცვლადი: ")
print(f"snake_case: {camel_to_snake(text)}")