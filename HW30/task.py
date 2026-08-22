import os
import sqlite3
import time

db_path = os.path.join(os.path.dirname(__file__), "library.db")
sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")


def delete_book_by_id(cursor, book_id):
    cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
    print(f"პროცედურა: წიგნი ID #{book_id} წაიშალა (წაშლილია: {cursor.rowcount} ჩანაწერი).")


def update_book_price_by_id(cursor, book_id, new_price):
    cursor.execute("UPDATE books SET price = ? WHERE id = ?", (new_price, book_id))
    print(f"პროცედურა: წიგნი ID #{book_id}-ს ფასი შეიცვალა -> ${new_price:.2f}")


with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    with open(sql_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    print("=================== 1. VIEW-ების გამოძახება ===================")

    print("\n--- 1.1 View: v_all_authors ---")
    cursor.execute("SELECT * FROM v_all_authors")
    for r in cursor.fetchall():
        print(r)

    print("\n--- 1.2 View: v_expensive_books (ფასი > 20) ---")
    cursor.execute("SELECT * FROM v_expensive_books")
    for r in cursor.fetchall():
        print(r)

    print("\n--- 1.3 View: v_books_with_authors ---")
    cursor.execute("SELECT * FROM v_books_with_authors")
    for r in cursor.fetchall():
        print(r)

    print("\n=================== 2. VIEW-ების განახლება (UPDATE) ===================")

    cursor.execute("DROP VIEW IF EXISTS v_expensive_books")
    cursor.execute("CREATE VIEW v_expensive_books AS SELECT * FROM books WHERE price > 30.00")
    print("\n--- 2.1 განახლებული View (ახალი ფილტრი: ფასი > 30) ---")
    cursor.execute("SELECT * FROM v_expensive_books")
    for r in cursor.fetchall():
        print(r)

    cursor.execute("DROP VIEW IF EXISTS v_expensive_books")
    cursor.execute("""
        CREATE VIEW v_expensive_books AS 
        SELECT id, title, price, (price * 0.9) AS discounted_price, published_year 
        FROM books 
        WHERE price > 30.00
    """)
    print("\n--- 2.2 განახლებული View (დამატებული სვეტი: discounted_price) ---")
    cursor.execute("SELECT * FROM v_expensive_books")
    for r in cursor.fetchall():
        print(r)

    print("\n=================== 3. VIEW-ების წაშლა ===================")
    cursor.execute("DROP VIEW IF EXISTS v_all_authors")
    cursor.execute("DROP VIEW IF EXISTS v_expensive_books")
    cursor.execute("DROP VIEW IF EXISTS v_books_with_authors")
    print("ყველა ვიუ წარმატებით წაიშალა.")

    print("\n=================== 4. პროცედურები და ტრიგერის ტესტი ===================")

    print("\n--- საწყისი მონაცემი წიგნი #1-ისთვის ---")
    cursor.execute("SELECT id, title, price, updated_at FROM books WHERE id = 1")
    print("საწყისი:", cursor.fetchone())

    time.sleep(1)

    update_book_price_by_id(cursor, 1, 29.99)
    conn.commit()

    print("--- განახლებული მონაცემი (ტრიგერმა ავტომატურად განაახლა updated_at) ---")
    cursor.execute("SELECT id, title, price, updated_at FROM books WHERE id = 1")
    print("განახლებული:", cursor.fetchone())

    delete_book_by_id(cursor, 2)
    conn.commit()