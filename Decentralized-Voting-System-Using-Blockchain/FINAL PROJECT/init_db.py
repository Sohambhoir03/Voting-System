import sqlite3

DB_FILE = 'database_new.db'  # Use a new name to avoid conflicts

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aadhar TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    has_voted BOOLEAN DEFAULT FALSE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    FOREIGN KEY (voter_id) REFERENCES users(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
)
''')

conn.commit()
conn.close()
print("New database created successfully as database_new.db!")