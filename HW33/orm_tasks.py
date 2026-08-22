import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from project.models import Author, Book, Reader

Reader.objects.all().delete()
Book.objects.all().delete()
Author.objects.all().delete()

author_data = [
    {
        "first_name": "Maya",
        "last_name": "Kandelaki",
        "email": "maya.kandelaki@example.com",
        "biography": "Modern fiction author.",
    },
    {
        "first_name": "Liam",
        "last_name": "Carter",
        "email": "liam.carter@example.com",
        "biography": "Writer of historical mysteries.",
    },
]
authors = [Author.objects.create(**data) for data in author_data]

book_data = [
    ("The Glass Harbor", "A story about memory and the sea.", 288, authors[0]),
    ("Paper Moons", "A quiet novel about changing cities.", 214, authors[0]),
    ("The Last Archive", "A mystery hidden inside an old library.", 352, authors[1]),
    ("Northbound", "A journey through unfamiliar landscapes.", 176, authors[1]),
]
books = [
    Book.objects.create(title=title, summary=summary, pages=pages, author=author)
    for title, summary, pages, author in book_data
]

reader_data = [
    ("Tako", "Maisuradze", "tako.reader@example.com", [books[0], books[2]]),
    ("Gio", "Beridze", "gio.reader@example.com", [books[1], books[3]]),
    ("Nana", "Lomidze", "nana.reader@example.com", [books[0], books[1], books[3]]),
]
readers = []
for first_name, last_name, email, selected_books in reader_data:
    reader = Reader.objects.create(first_name=first_name, last_name=last_name, email=email)
    reader.books.set(selected_books)
    readers.append(reader)

print("--- Authors ---")
for author in Author.objects.all():
    print(f"{author} | {author.email}")

print("\n--- Books and authors ---")
for book in Book.objects.select_related("author"):
    print(f"{book.title} | {book.author} | {book.pages} pages")

print("\n--- Readers and books ---")
for reader in Reader.objects.prefetch_related("books"):
    titles = ", ".join(book.title for book in reader.books.all())
    print(f"{reader}: {titles}")

selected_reader = Reader.objects.get(email="tako.reader@example.com")
selected_reader.first_name = "Tamuna"
selected_reader.save()

books[0].pages = 300
books[0].save()

selected_reader.books.add(books[3])
selected_reader.books.remove(books[2])

reader_to_delete = Reader.objects.get(email="nana.reader@example.com")
reader_to_delete.delete()

Book.objects.get(title="Northbound").delete()
Author.objects.get(email="liam.carter@example.com").delete()

print("\n--- Updated library ---")
print(f"Authors: {Author.objects.count()}")
print(f"Books: {Book.objects.count()}")
print(f"Readers: {Reader.objects.count()}")
