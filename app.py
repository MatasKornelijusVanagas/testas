import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = 'tasks.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        user TEXT,
        status TEXT
    )
    ''')
    db.commit()

@app.route('/')
def index():
    db = get_db()
    init_db()  # Ensure the database and table are initialized
    cur = db.cursor()
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    return render_template('index.html', tasks=tasks)

@app.route('/task/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        db = get_db()
        init_db()  # Ensure the database and table are initialized
        db.execute('INSERT INTO tasks (title, description, user, status) VALUES (?, ?, ?, ?)',
                   [request.form['title'], request.form['description'], request.form['user'], 'Pending'])
        db.commit()
        return redirect(url_for('index'))
    return render_template('add_task.html')

@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    db = get_db()
    init_db()  # Ensure the database and table are initialized
    if request.method == 'POST':
        db.execute('UPDATE tasks SET title = ?, description = ?, user = ?, status = ? WHERE id = ?',
                   [request.form['title'], request.form['description'], request.form['user'], request.form['status'], task_id])
        db.commit()
        return redirect(url_for('index'))
    else:
        cur = db.cursor()
        cur.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cur.fetchone()
        return render_template('edit_task.html', task=task)

@app.route('/task/delete/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    db = get_db()
    init_db()  # Ensure the database and table are initialized
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

