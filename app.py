import os
import sqlite3

import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Laboratory Activities 8 and 9: the partner's deployed API, written here in the code.
# Change this one line if your partner changes. PARTNER_API_URL is only for testing on one PC.
PARTNER_URL = os.environ.get(
    "PARTNER_API_URL",
    "https://noemi-act-9.onrender.com/api/students"
)


# Laboratory Activity 7: connect to the SQLite database made by init_db.py
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# Laboratory Activity 9, Step 2: a database made in Activity 7 has no "source" column. Add it once.
def ensure_source_column():
    conn = get_db_connection()
    columns = [c['name'] for c in conn.execute('PRAGMA table_info(students)')]

    if columns and 'source' not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'")
        conn.execute("UPDATE students SET source = 'Local' WHERE source IS NULL")
        conn.commit()

    conn.close()


ensure_source_column()


@app.route('/')
def home():
    return render_template('index.html', partner_url=PARTNER_URL)


# Check a student sent from the web page before it touches the database.
def clean_student(data):
    if not isinstance(data, dict):
        return None, 'Send the student information as JSON.'

    for field in ['student_id', 'name', 'program', 'year', 'section']:
        if str(data.get(field, '')).strip() == '':
            return None, field + ' is required.'

    try:
        year = int(data['year'])
    except (TypeError, ValueError):
        return None, 'Year must be a number.'

    if year < 1:
        return None, 'Year must be 1 or more.'

    return (
        str(data['student_id']).strip(),
        str(data['name']).strip(),
        str(data['program']).strip(),
        year,
        str(data['section']).strip()
    ), None


@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00271",
        "name": "Rochelle Ann Paclibar",
        "program": "BSIT",
        "year": 3,
        "section": "Dijkstra"
    })


@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })


# Custom API endpoint for Laboratory Activity 6
@app.route('/course')
def get_course():
    return jsonify({
        "course_code": "IT 3120",
        "course_name": "System Integration",
        "program": "BSIT",
        "year": 3
    })


# Laboratory Activity 7: all students from the database
@app.route('/students')
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# Laboratory Activity 7: one student by database ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# Laboratory Activity 7 additional task: students in one section (read from the database)
@app.route('/students/section/<section>')
def get_students_by_section(section):
    conn = get_db_connection()
    students = conn.execute(
        'SELECT * FROM students WHERE LOWER(section) = LOWER(?)', (section,)
    ).fetchall()
    conn.close()

    return jsonify([dict(student) for student in students])


# Laboratory Activity 8, Step 6: all records as JSON (read by the classmate)
@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM students').fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


# Laboratory Activity 8, Step 2: CREATE.
# Laboratory Activity 9, Step 8: a record sent without a source is labelled "External API".
# The web page always sends "Local" for records you add yourself.
@app.route('/api/students', methods=['POST'])
def add_student():
    values, error = clean_student(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    source = str(request.get_json(silent=True).get('source') or 'External API').strip()

    conn = get_db_connection()
    cursor = conn.execute(
        """INSERT INTO students
        (student_id, name, program, year, section, source)
        VALUES (?, ?, ?, ?, ?, ?)""",
        values + (source,)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"message": "Student added", "id": new_id}), 201


# Laboratory Activity 8, Step 3: READ one
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()
    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# Laboratory Activity 8, Step 3: UPDATE
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    values, error = clean_student(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        """UPDATE students SET student_id=?, name=?, program=?,
        year=?, section=? WHERE id=?""",
        values + (id,)
    )
    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student updated"})


# Laboratory Activity 8, Step 3: DELETE
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    changed = cursor.rowcount
    conn.close()

    if changed == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted"})


# Laboratory Activity 9, Step 3: Flask retrieves the partner's API (browsers cannot always call
# another website directly because of cross-origin rules). Read-only: this route only sends a GET.
@app.route('/partner-records')
def partner_records():
    try:
        response = requests.get(PARTNER_URL, timeout=60, allow_redirects=False)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return jsonify({"error": "Unable to retrieve partner data"}), 502

    if not isinstance(data, list):
        return jsonify({"error": "Unable to retrieve partner data"}), 502

    return jsonify(data)


# Laboratory Activity 9, Step 5: save one selected partner record into my own database
@app.route('/import-student', methods=['POST'])
def import_student():
    values, error = clean_student(request.get_json(silent=True))

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()
    conn.execute(
        """INSERT INTO students
        (student_id, name, program, year, section, source)
        VALUES (?, ?, ?, ?, ?, ?)""",
        values + ('Classmate API',)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Remote record saved"}), 201


# Laboratory Activity 9, Step 9: send one practice record to the partner's POST /api/students
@app.route('/send-record', methods=['POST'])
def send_record():
    body = request.get_json(silent=True) or {}
    values, error = clean_student(body.get('record'))

    if error:
        return jsonify({"error": error}), 400

    record = {
        "student_id": values[0], "name": values[1], "program": values[2],
        "year": values[3], "section": values[4], "source": "Partner API"
    }

    try:
        response = requests.post(PARTNER_URL, json=record, timeout=60, allow_redirects=False)
    except requests.RequestException:
        return jsonify({"error": "Unable to reach the partner API"}), 502

    result = {
        "partner_status": response.status_code,
        "partner_response": response.text.strip(),
        "sent": record
    }

    if response.status_code >= 400:
        result["error"] = "Partner replied " + str(response.status_code) + ": " + response.text[:200]
        return jsonify(result), response.status_code

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)