def process_text(text):
    upper_count = sum(1 for ch in text if ch.isupper())
    return upper_count, text.upper()

text = input("შეიყვანეთ ტექსტი: ")
count, upper_text = process_text(text)

print(f"დიდი ასოები: {count}")
print(f"ტექსტი: {upper_text}")