import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "company.db")
sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")

with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    with open(sql_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    print("=== 1. საშუალოზე მეტი ხელფასის მქონე თანამშრომლები (Subquery) ===")
    cursor.execute("""
        SELECT name, salary 
        FROM employees 
        WHERE salary > (SELECT AVG(salary) FROM employees)
    """)
    for r in cursor.fetchall():
        print(f"თანამშრომელი: {r[0]}, ხელფასი: ${r[1]}")

    print("\n=== 2. სახელი, ხელფასი და დეპარტამენტი JOIN-ის გარეშე (Scalar Subquery) ===")
    cursor.execute("""
        SELECT name, salary, 
               (SELECT name FROM departments WHERE departments.id = employees.department_id) AS department_name 
        FROM employees
    """)
    for r in cursor.fetchall():
        print(f"{r[0]} | ${r[1]} | დეპარტამენტი: {r[2]}")

    print("\n=== 3. New York-ის დეპარტამენტების თანამშრომლები (IN Subquery) ===")
    cursor.execute("""
        SELECT name, salary 
        FROM employees 
        WHERE department_id IN (SELECT id FROM departments WHERE location = 'New York')
    """)
    for r in cursor.fetchall():
        print(f"{r[0]} (${r[1]})")

    print("\n=== 4. დეპარტამენტები მინიმუმ 1 თანამშრომლით (EXISTS) ===")
    cursor.execute("""
        SELECT name, location 
        FROM departments d 
        WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id)
    """)
    for r in cursor.fetchall():
        print(f"აქტიური დეპარტამენტი: {r[0]} ({r[1]})")

    print("\n=== 5. ხელფასი > Marketing-ის მინიმალურ ხელფასზე (> ANY) ===")
    cursor.execute("""
        SELECT name, salary 
        FROM employees 
        WHERE salary > (SELECT MIN(salary) FROM employees WHERE department_id = (SELECT id FROM departments WHERE name = 'Marketing'))
    """)
    for r in cursor.fetchall():
        print(f"{r[0]} (${r[1]})")

    print("\n=== 6. ხელფასი > IT-ის მაქსიმალურ ხელფასზე (> ALL) ===")
    cursor.execute("""
        SELECT name, salary 
        FROM employees 
        WHERE salary > (SELECT MAX(salary) FROM employees WHERE department_id = (SELECT id FROM departments WHERE name = 'IT'))
    """)
    rows_all = cursor.fetchall()
    print(rows_all if rows_all else "არავინაა (ყველაზე მაღალი ხელფასი IT-შია)")

    print("\n=== 7. New York ან Los Angeles თანამშრომლები (UNION - დუბლიკატების გარეშე) ===")
    cursor.execute("""
        SELECT e.name, e.salary, d.location 
        FROM employees e JOIN departments d ON e.department_id = d.id 
        WHERE d.location = 'New York'
        UNION
        SELECT e.name, e.salary, d.location 
        FROM employees e JOIN departments d ON e.department_id = d.id 
        WHERE d.location = 'Los Angeles'
    """)
    for r in cursor.fetchall():
        print(f"{r[0]} - ${r[1]} ({r[2]})")

    print("\n=== 8. იგივე მოთხოვნა (UNION ALL - დუბლიკატებით) ===")
    cursor.execute("""
        SELECT e.name, e.salary, d.location 
        FROM employees e JOIN departments d ON e.department_id = d.id 
        WHERE d.location = 'New York'
        UNION ALL
        SELECT e.name, e.salary, d.location 
        FROM employees e JOIN departments d ON e.department_id = d.id 
        WHERE d.location = 'Los Angeles'
    """)
    for r in cursor.fetchall():
        print(f"{r[0]} - ${r[1]} ({r[2]})")