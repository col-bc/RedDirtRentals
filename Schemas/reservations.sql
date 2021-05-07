CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    confirmation_num TEXT NOT NULL,
    rental_id INT NOT NULL,
    customer_id INT NOT NULL,
    
    pref_start_1 DATE NOT NULL,
    pref_start_2 DATE NOT NULL,
    pref_start_3 DATE NOT NULL,
    pref_end_1 DATE NOT NULL,
    pref_end_2 DATE NOT NULL,
    pref_end_3 DATE NOT NULL,

    status TEXT DEFAULT 'PENDING'
);