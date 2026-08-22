import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "cars.db")
sql_path = os.path.join(os.path.dirname(__file__), "cars.sql")

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()

    # 1. ცხრილის შექმნა და 10 ჩანაწერის შეტანა
    with open(sql_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    print("=== 1. მონაცემთა გამოტანა (SELECT) ===")

    # 1.1 ყველა მონაცემის ყველა სვეტი
    print("\n--- 1.1 ყველა მონაცემი ---")
    cursor.execute("SELECT id, brand, model, year, vin, engine_capacity, mileage, is_customs_cleared, price, is_sold FROM cars")
    for r in cursor.fetchall():
        print(r)

    # 1.2 ბრენდი, მოდელი, წელი, ფასი
    print("\n--- 1.2 ბრენდი, მოდელი, წელი, ფასი ---")
    cursor.execute("SELECT brand, model, year, price FROM cars")
    for r in cursor.fetchall():
        print(r)

    # 1.3 კონკრეტული ბრენდი (BMW)
    print("\n--- 1.3 ბრენდი = BMW ---")
    cursor.execute("SELECT * FROM cars WHERE brand = 'BMW'")
    for r in cursor.fetchall():
        print(r)

    # 1.4 ფასი 20000 და 50000 შორის
    print("\n--- 1.4 ფასი 20000 და 50000 შორის ---")
    cursor.execute("SELECT brand, model, price FROM cars WHERE price BETWEEN 20000 AND 50000")
    for r in cursor.fetchall():
        print(r)

    # 1.5 წელი > 2010 და განბაჟებული
    print("\n--- 1.5 წელი > 2010 და განბაჟებული ---")
    cursor.execute("SELECT brand, model, year, is_customs_cleared FROM cars WHERE year > 2010 AND is_customs_cleared = 1")
    for r in cursor.fetchall():
        print(r)

    print("\n=== 2. მონაცემთა წაშლა (DELETE & DROP) ===")

    # 2.1 პირველი ორი მონაცემის წაშლა ID-ით ერთ ქვერიში
    cursor.execute("DELETE FROM cars WHERE id IN (SELECT id FROM cars ORDER BY id LIMIT 2)")
    print(f"2.1 წაიშალა პირველი ორი ჩანაწერი (წაშლილია: {cursor.rowcount})")

    # 2.2 ყველა გაყიდული მანქანის წაშლა
    cursor.execute("DELETE FROM cars WHERE is_sold = 1")
    print(f"2.2 წაიშალა გაყიდული მანქანები (წაშლილია: {cursor.rowcount})")

    # 2.3 ყველა მონაცემის წაშლა (ცხრილის გასუფთავება)
    cursor.execute("DELETE FROM cars")
    print("2.3 ცხრილი გასუფთავდა ყველა მონაცემისგან.")

    # 2.4 ცხრილის წაშლა
    cursor.execute("DROP TABLE IF EXISTS cars")
    print("2.4 ცხრილი 'cars' წაიშალა.")