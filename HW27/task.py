import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "hotel.db")
sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")

with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    with open(sql_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    print("=================== 1. SQL მოთხოვნები (SELECT) ===================")

    print("\n--- 1. ყველა ნომერი სასტუმროს სახელთან ერთად ---")
    cursor.execute("""
        SELECT rooms.room_number, rooms.floor, rooms.price_per_night, hotels.name AS hotel_name
        FROM rooms
        JOIN hotels ON rooms.hotel_id = hotels.id
    """)
    for r in cursor.fetchall():
        print(f"ოთახი #{r[0]} (სართული {r[1]}, ფასი: ${r[2]}) -> სასტუმრო: {r[3]}")

    print("\n--- 2. ყველა სტუმარი ნომრითა და სასტუმროთი ---")
    cursor.execute("""
        SELECT guests.first_name, guests.last_name, guests.phone, rooms.room_number, hotels.name
        FROM guests
        JOIN rooms ON guests.room_id = rooms.id
        JOIN hotels ON rooms.hotel_id = hotels.id
    """)
    for r in cursor.fetchall():
        print(f"სტუმარი: {r[0]} {r[1]} ({r[2]}) -> ოთახი: {r[3]}, სასტუმრო: {r[4]}")

    print("\n--- 3. 'Radisson Blu Iveria'-ს სტუმრები ---")
    cursor.execute("""
        SELECT guests.first_name, guests.last_name, hotels.name
        FROM guests
        JOIN rooms ON guests.room_id = rooms.id
        JOIN hotels ON rooms.hotel_id = hotels.id
        WHERE hotels.name = 'Radisson Blu Iveria'
    """)
    for r in cursor.fetchall():
        print(f"{r[0]} {r[1]} ({r[2]})")

    print("\n--- 4. თითო სასტუმროში ნომრების რაოდენობა ---")
    cursor.execute("""
        SELECT hotels.name, COUNT(rooms.id) AS room_count
        FROM hotels
        LEFT JOIN rooms ON hotels.id = rooms.hotel_id
        GROUP BY hotels.id, hotels.name
    """)
    for r in cursor.fetchall():
        print(f"{r[0]}: {r[1]} ნომერი")

    print("\n--- 5. ნომრები სერვისის გარეშე ---")
    cursor.execute("""
        SELECT rooms.room_number, rooms.floor, hotels.name
        FROM rooms
        JOIN hotels ON rooms.hotel_id = hotels.id
        LEFT JOIN services ON rooms.id = services.room_id
        WHERE services.id IS NULL
    """)
    for r in cursor.fetchall():
        print(f"ნომერი #{r[0]} (სართული {r[1]}), სასტუმრო: {r[2]}")

    print("\n=================== 2. ცვლილებების ოპერაციები ===================")

    print("\n--- 2.1 ნომერი #1-ის წაშლა და CASCADE ეფექტი ---")
    cursor.execute("DELETE FROM rooms WHERE id = 1")
    conn.commit()

    cursor.execute("SELECT count(*) FROM guests WHERE room_id = 1")
    remaining_guests = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM services WHERE room_id = 1")
    remaining_services = cursor.fetchone()[0]
    print(f"ნომერი #1 წაიშალა. დარჩენილი სტუმრები ამ ნომერზე: {remaining_guests}, დარჩენილი სერვისები: {remaining_services} (CASCADE მუშაობს!)")

    print("\n--- 2.2 ოთახი #2-ის ფასის შეცვლა ---")
    cursor.execute("UPDATE rooms SET price_per_night = 499.00 WHERE id = 2")
    conn.commit()
    cursor.execute("SELECT room_number, price_per_night FROM rooms WHERE id = 2")
    updated_room = cursor.fetchone()
    print(f"ოთახი #{updated_room[0]} ახალი ფასი: ${updated_room[1]}")

    print("\n--- 2.3 სტუმრის სხვა ნომერზე გადაწერა ---")
    cursor.execute("UPDATE guests SET room_id = 3 WHERE first_name = 'Luka'")
    conn.commit()
    cursor.execute("""
        SELECT guests.first_name, guests.last_name, rooms.room_number
        FROM guests
        JOIN rooms ON guests.room_id = rooms.id
        WHERE guests.first_name = 'Luka'
    """)
    updated_guest = cursor.fetchone()
    print(f"სტუმარი {updated_guest[0]} {updated_guest[1]} წარმატებით გადავიდა ოთახში #{updated_guest[2]}")