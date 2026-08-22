PRAGMA foreign_keys = ON;

DROP VIEW IF EXISTS v_books_with_authors;
DROP VIEW IF EXISTS v_expensive_books;
DROP VIEW IF EXISTS v_all_authors;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;

CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title VARCHAR(150) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    published_year INTEGER NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

INSERT INTO authors (name, country) VALUES
('George Orwell', 'United Kingdom'),
('Fyodor Dostoevsky', 'Russia'),
('Gabriel Garcia Marquez', 'Colombia');

INSERT INTO books (author_id, title, price, published_year) VALUES
(1, '1984', 25.00, 1949),
(1, 'Animal Farm', 18.00, 1945),
(2, 'Crime and Punishment', 35.00, 1866),
(2, 'The Brothers Karamazov', 40.00, 1880),
(3, 'One Hundred Years of Solitude', 30.00, 1967);

CREATE TRIGGER trg_books_update_timestamp 
AFTER UPDATE ON books
FOR EACH ROW
BEGIN
    UPDATE books 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = OLD.id;
END;

CREATE VIEW v_all_authors AS
SELECT * FROM authors;

CREATE VIEW v_expensive_books AS
SELECT * FROM books WHERE price > 20.00;

CREATE VIEW v_books_with_authors AS
SELECT b.id AS book_id, b.title, b.price, b.published_year, b.updated_at,
       a.id AS author_id, a.name AS author_name, a.country
FROM books b
JOIN authors a ON b.author_id = a.id;