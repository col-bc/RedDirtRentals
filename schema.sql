CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    make TEXT,
    model TEXT,
    fuel_type TEXT,
    horsepower TEXT, 
    deck_size TEXT,
    implements TEXT,
    stock TEXT,
    drive TEXT,
    rate FLOAT,
    image_paths BLOB,
    job_category TEXT,
    price_range TEXT, 
    is_available INTEGER DEFAULT 1,
    available_on DATE,
    rented_by TEXT,
    rent_queue TEXT
    is_shown INTEGER DEFAULT 1,
    description TEXT,
    features TEXT
);