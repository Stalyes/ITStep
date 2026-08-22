import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "ecommerce.db")
sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")

with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # სქემის და მონაცემების შეტანა
    with open(sql_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    print("=== 1. მომხმარებლები და One-to-One პროფილები ===")
    cursor.execute("""
        SELECT c.id, c.name, c.email, p.phone, p.address
        FROM customers c
        LEFT JOIN customer_profiles p ON c.id = p.customer_id
    """)
    for r in cursor.fetchall():
        print(f"#{r[0]} {r[1]} ({r[2]}) | ტელ: {r[3]}, მისამართი: {r[4]}")

    print("\n=== 2. მომწოდებლები და One-to-Many პროდუქტები ===")
    cursor.execute("""
        SELECT s.name, p.name, p.price
        FROM suppliers s
        JOIN products p ON s.id = p.supplier_id
        ORDER BY s.name
    """)
    for r in cursor.fetchall():
        print(f"მომწოდებელი: {r[0]} -> პროდუქტი: {r[1]} (${r[2]})")

    print("\n=== 3. შეკვეთების დეტალები (Many-to-Many პროდუქტებთან და რაოდენობასთან) ===")
    cursor.execute("""
        SELECT o.id, c.name, p.name, oi.quantity, p.price, (oi.quantity * p.price) AS total_item_price
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        ORDER BY o.id
    """)
    for r in cursor.fetchall():
        print(f"შეკვეთა #{r[0]} | მყიდველი: {r[1]} | {r[2]} x {r[3]} (თითო: ${r[4]:.2f}) = ${r[5]:.2f}")

    print("\n=== 4. შეკვეთების სრული ჯამური ღირებულება ===")
    cursor.execute("""
        SELECT o.id, c.name, SUM(oi.quantity * p.price) AS order_total
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN order_items oi ON o.id = oi.order_id
        JOIN products p ON oi.product_id = p.id
        GROUP BY o.id, c.name
    """)
    for r in cursor.fetchall():
        print(f"შეკვეთა #{r[0]} ({r[1]}) - სულ ჯამი: ${r[2]:.2f}")