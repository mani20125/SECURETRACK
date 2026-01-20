DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS couriers;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE couriers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_id TEXT UNIQUE NOT NULL,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    courier_id INTEGER,
    latitude REAL,
    longitude REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (courier_id) REFERENCES couriers (id)
);
