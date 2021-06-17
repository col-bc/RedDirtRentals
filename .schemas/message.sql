CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    to_id INTEGER NOT NULL,
    from_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT "New"
);