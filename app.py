from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database Initialization
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS topics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        completed INTEGER DEFAULT 0,
                        finished_at TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS subtopics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic_id INTEGER,
                        name TEXT,
                        completed INTEGER DEFAULT 0,
                        FOREIGN KEY(topic_id) REFERENCES topics(id))''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics")
    topics = cursor.fetchall()

    topic_data = []
    for topic in topics:
        cursor.execute("SELECT * FROM subtopics WHERE topic_id=?", (topic[0],))
        subtopics = cursor.fetchall()
        topic_data.append({"id": topic[0], "name": topic[1], "completed": topic[2], "finished_at": topic[3], "subtopics": subtopics})

    conn.close()
    return render_template("index.html", topics=topic_data)

@app.route('/add_topic', methods=['POST'])
def add_topic():
    topic_name = request.form.get("topic_name")
    subtopics = request.form.getlist("subtopics[]")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO topics (name) VALUES (?)", (topic_name,))
    topic_id = cursor.lastrowid

    for subtopic in subtopics:
        cursor.execute("INSERT INTO subtopics (topic_id, name) VALUES (?, ?)", (topic_id, subtopic))

    conn.commit()
    conn.close()
    
    return redirect('/')

@app.route('/update', methods=['POST'])
def update():
    subtopic_id = request.form.get("subtopic_id")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("UPDATE subtopics SET completed=1 WHERE id=?", (subtopic_id,))
    
    cursor.execute("SELECT topic_id FROM subtopics WHERE id=?", (subtopic_id,))
    topic_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM subtopics WHERE topic_id=? AND completed=0", (topic_id,))
    remaining = cursor.fetchone()[0]

    if remaining == 0:
        finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE topics SET completed=1, finished_at=? WHERE id=?", (finished_at, topic_id))

    conn.commit()
    conn.close()
    return jsonify({"status": "updated"})

if __name__ == "__main__":
    app.run(debug=True)
