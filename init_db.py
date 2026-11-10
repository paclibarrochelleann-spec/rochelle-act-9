import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
''')

cursor.execute("DELETE FROM students")

# Start the IDs at 1 again, so /students/1 still works every time you re-run this file.
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'students'")

# Sample records (fictional, non-sensitive). Every record made here has the source 'Local' (Activity 9).
# They use different student IDs and names, and more than one program, year level and section.
students = [
    ('24-00271', 'Rochelle Ann Paclibar', 'BSIT', 3, 'Dijkstra', 'Local'),
    ('24-00272', 'Marco Villanueva', 'BSIT', 3, 'Dijkstra', 'Local'),
    ('24-00273', 'Liza Fernandez', 'BSIT', 3, 'Kruskal', 'Local'),
    ('24-00274', 'Carlo Mendoza', 'BSCS', 2, 'Kruskal', 'Local'),
    ('24-00275', 'Anna Beltran', 'BSCS', 2, 'Dijkstra', 'Local'),
    ('24-00276', 'Daniel Ocampo', 'BSIS', 1, 'Kruskal', 'Local'),
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section, source)
VALUES (?, ?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
