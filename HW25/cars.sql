DROP TABLE IF EXISTS cars;

CREATE TABLE cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    vin VARCHAR(17) NOT NULL UNIQUE CHECK (length(vin) <= 17),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    engine_capacity DECIMAL(3, 1) CHECK (engine_capacity > 0.5),
    mileage INTEGER CHECK (mileage IS NULL OR mileage >= 0),
    is_customs_cleared BOOLEAN NOT NULL DEFAULT 0 CHECK (is_customs_cleared IN (0, 1)),
    price DECIMAL(10, 2),
    description TEXT,
    is_sold BOOLEAN NOT NULL DEFAULT 0 CHECK (is_sold IN (0, 1))
);

INSERT INTO cars
    (brand, model, year, vin, engine_capacity, mileage,
     is_customs_cleared, price, description, is_sold)
VALUES
    ('BMW', 'M5 F90', 2021, 'WBAJB91000B123456', 4.4, 35000,
     1, 75000.00, 'იდეალურ მდგომარეობაში, სრული კომპლექტაციით', 0),
    ('Mercedes-Benz', 'E63s AMG', 2020, 'WDDZF8KB5LA654321', 4.0, 42000,
     1, 68000.00, 'გავლილი აქვს სრული სერვისი ცენტრში', 0),
    ('Audi', 'RS6 Avant', 2022, 'WAUZZZF27NA112233', 4.0, 18000,
     1, 95000.00, 'ქარხნული საღებავი, კერამიკული მუხრუჭებით', 0),
    ('Porsche', '911 Carrera S', 2019, 'WP0AB2A99KS123987', 3.0, 29000,
     1, 89000.00, 'Sport Chrono პაკეტით', 1),
    ('Toyota', 'Camry', 2022, '4T1B11HK5NU789456', 2.5, 55000,
     1, 24000.00, 'ჰიბრიდი, ძალიან ეკონომიური და გამძლე', 0),
    ('Lexus', 'GX460', 2018, 'JTJJM7FX7J5456123', 4.6, 95000,
     1, 38000.00, 'კარგ მდგომარეობაში, 7 ადგილიანი', 0),
    ('Ford', 'Mustang GT', 2017, '1FA6P8CF8H5987321', 5.0, 78000,
     0, 19500.00, 'ახალი ჩამოყვანილია ამერიკიდან, დაუზიანებელი', 0),
    ('Volkswagen', 'Golf R', 2021, 'WVWZZZCDZMW334455', 2.0, 31000,
     1, 32000.00, '4Motion სრული ამძრაობა, Akrapovic მაყუჩით', 0),
    ('Tesla', 'Model 3 Performance', 2022, '5YJ3E1EB8NF556677', 1.0, 22000,
     1, 36000.00, 'Full Self-Driving პაკეტით, იდეალურ მდგომარეობაში', 1),
    ('Subaru', 'WRX STI', 2019, 'JF1VA1E68K8778899', 2.5, 60000,
     1, 27500.00, 'ორიგინალი გარბენი, ტუნინგის გარეშე', 0);