CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INT NOT NULL,
    customer_id INT NOT NULL,
    date_from DATE,
    date_to DATE,
    status TEXT
);