CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
Y    category TEXT,
Y    make TEXT,
Y    model TEXT,
Y    fuel_type TEXT,
Y    horsepower TEXT, 
Y    deck_size TEXT,
    implements TEXT,
Y    stock TEXT,
Y    drive TEXT,
Y    rate FLOAT,
Y    image_paths BLOB,
Y    job_category TEXT,
Y    price_range TEXT, 
Y    is_available INTEGER DEFAULT 1,
Y    available_on DATE,
Y    rented_by TEXT,
Y    rent_queue TEXT
Y    is_shown INTEGER DEFAULT 1,
Y    description TEXT,
Y    features TEXT
);