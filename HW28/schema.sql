PRAGMA foreign_keys = ON;

-- ძველი ცხრილების წაშლა
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS customer_profiles;
DROP TABLE IF EXISTS customers;

-- 1. მომხმარებლები (customers)
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- 2. მომხმარებლის პროფილი (customer_profiles) - One-to-One კავშირი
CREATE TABLE customer_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(200),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- 3. მომწოდებლები (suppliers)
CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100) UNIQUE NOT NULL
);

-- 4. პროდუქტები (products) - One-to-Many suppliers-თან
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    supplier_id INTEGER NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- =============================================
-- სატესტო მონაცემები
-- =============================================

-- მომხმარებლები და მათი 1-to-1 პროფილები
INSERT INTO customers (name, email) VALUES
('Nika Papaskiri', 'nika@example.com'),
('Mariam Kapanadze', 'mariam@example.com');

INSERT INTO customer_profiles (customer_id, phone, address) VALUES
(1, '+995599111222', 'Tbilisi, Rustaveli Ave 10'),
(2, '+995599333444', 'Batumi, Chavchavadze St 25');

-- მომწოდებლები
INSERT INTO suppliers (name, contact_email) VALUES
('TechSupplier Ltd', 'contact@techsupplier.ge'),
('OfficeWorld Georgia', 'info@officeworld.ge');

-- პროდუქტები (1-to-Many მომწოდებელთან)
INSERT INTO products (name, price, supplier_id) VALUES
('MacBook Pro 16', 2500.00, 1),
('Dell UltraSharp Monitor', 450.00, 1),
('Logitech MX Master 3', 100.00, 1),
('Ergonomic Office Chair', 320.00, 2),
('Standing Desk', 600.00, 2);

-- შეკვეთები (1-to-Many მომხმარებელთან)
INSERT INTO orders (customer_id) VALUES
(1), -- Nika-ს შეკვეთა #1
(1), -- Nika-ს შეკვეთა #2
(2); -- Mariam-ის შეკვეთა #3

-- შეკვეთის პროდუქტები (Many-to-Many შუამავალი ცხრილი რაოდენობით)
INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1), -- შეკვეთა 1: 1 ცალი MacBook
(1, 3, 2), -- შეკვეთა 1: 2 ცალი მაუსი
(2, 4, 1), -- შეკვეთა 2: 1 ცალი სკამი
(3, 2, 2), -- შეკვეთა 3: 2 ცალი მონიტორი
(3, 5, 1); -- შეკვეთა 3: 1 ცალი მაგიდა