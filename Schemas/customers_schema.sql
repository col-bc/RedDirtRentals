CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    address TEXT,
    city TEXT,
    state TEXT,
    ZIP TEXT,
    
    phonenumber TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    token_name TEXT,
    token TEXT,

    selected_inventory_id INTEGER,
    selected_date_from DATE NOT NULL,
    selected_date_to DATE NOT NULL

);