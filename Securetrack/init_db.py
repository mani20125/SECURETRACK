import sqlite3

conn = sqlite3.connect('database.db')
with open('schema.sql') as f:
    conn.executescript(f.read())

cur = conn.cursor()
cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'password'))
cur.execute("INSERT INTO couriers (tracking_id, sender, receiver) VALUES (?, ?, ?)",
            ('TRACK123', 'Sender A, Hyderabad', 'Receiver B, Bangalore'))
cur.execute("INSERT INTO locations (courier_id, latitude, longitude) VALUES (?, ?, ?)",
            (1, 17.3850, 78.4867))
conn.commit()
conn.close()
print("Database created with sample data!")
