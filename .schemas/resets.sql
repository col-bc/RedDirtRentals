CREATE TABLE resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token BLOB NOT NULL,
    token_expiration BLOB NOT NULL,
    userid INT NOT NULL,
    used INTEGER DEFAULT 0
);