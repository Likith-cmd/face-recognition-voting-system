import sqlite3

conn = sqlite3.connect('voting system.db')
c = conn.cursor()

# Create voters table
c.execute('''
CREATE TABLE IF NOT EXISTS voters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    encoding BLOB NOT NULL,
    has_voted INTEGER DEFAULT 0
)
''')

# Create candidates table
c.execute('''
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    party TEXT NOT NULL,
    image_path TEXT
)
''')

# Create votes table
c.execute('''
CREATE TABLE IF NOT EXISTS votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id TEXT NOT NULL,
    candidate_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(voter_id) REFERENCES voters(voter_id),
    FOREIGN KEY(candidate_id) REFERENCES candidates(id)
)
''')

# Create admins table
c.execute('''
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ Database initialized with all required tables.")
