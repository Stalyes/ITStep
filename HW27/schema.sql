-- Foreign Keys გააქტიურება
PRAGMA foreign_keys = ON;

-- ძველი ცხრილების წაშლა (თუ არსებობს)
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS guests;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS hotels;

-- 1. სასტუმროები (hotels)
CREATE TABLE hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    stars INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5)
);

-- 2. ნომრები (rooms) - One-to-Many hotels-თან
CREATE TABLE rooms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel_id INTEGER NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    floor INTEGER NOT NULL,
    price_per_night DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels(id) ON DELETE CASCADE
);

-- 3. სტუმრები (guests) - One-to-Many rooms-თან
CREATE TABLE guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

-- 4. სერვისები (services) - One-to-Many rooms-თან
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);

-- =============================================
-- მონაცემების შეტანა
-- =============================================

-- 2 სასტუმრო
INSERT INTO hotels (name, city, stars) VALUES
('Radisson Blu Iveria', 'Tbilisi', 5),
('Rooms Hotel Kazbegi', 'Stepantsminda', 4);

-- თითო სასტუმროზე ნომრები (სულ 7 ნომერი)
INSERT INTO rooms (hotel_id, room_number, floor, price_per_night) VALUES
(1, '101', 1, 350.00),
(1, '201', 2, 450.00),
(1, '301', 3, 600.00),
(2, '102', 1, 280.00),
(2, '202', 2, 320.00),
(2, '302', 3, 400.00),
(2, '402', 4, 500.00); -- ნომერი სერვისის გარეშე (ტესტირებისთვის)

-- სტუმრები (მინიმუმ 2 თითო ნომერზე)
INSERT INTO guests (room_id, first_name, last_name, phone) VALUES
(1, 'Giorgi', 'Kapanadze', '+995599112233'),
(1, 'Nino', 'Beridze', '+995599223344'),
(2, 'Luka', 'Maisuradze', '+995599334455'),
(2, 'Mariam', 'Gelashvili', '+995599445566'),
(3, 'Davit', 'Abashidze', '+995599556677'),
(3, 'Salome', 'Chkheidze', '+995599667788'),
(4, 'Irakli', 'Lomidze', '+995599778899'),
(4, 'Tamar', 'Kvaratskhelia', '+995599889900'),
(5, 'Zura', 'Nozadze', '+995599001122'),
(5, 'Ana', 'Tsiklauri', '+995599113355'),
(6, 'Vakho', 'Shengelia', '+995599224466'),
(6, 'Nutsa', 'Bibilashvili', '+995599335577'),
(7, 'Giga', 'Javakhishvili', '+995599446688'),
(7, 'Elene', 'Kiknadze', '+995599557799');

-- სერვისები (მინიმუმ 2 თითო ნომერზე)
INSERT INTO services (room_id, service_name, cost) VALUES
(1, 'Room Service Breakfast', 45.00),
(1, 'Spa & Sauna', 90.00),
(2, 'Airport Transfer', 70.00),
(2, 'Mini Bar Refill', 35.00),
(3, 'Dry Cleaning', 50.00),
(3, 'Late Check-out', 60.00),
(4, 'Kazbegi Mountain Tour', 120.00),
(4, 'Dinner Buffet', 80.00),
(5, 'Massage', 100.00),
(5, 'Laundry Service', 40.00),
(6, 'Pool Access & Cocktail', 55.00),
(6, 'Breakfast in Bed', 45.00);