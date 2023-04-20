from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from datetime import timezone


import base64
import uuid
import sqlite3
import hashlib
import os

# Set up application configuration
UPLOAD_FOLDER = 'static/uploads'
app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)  # Add this line to add the zip function to Jinja2 globals
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user_data = c.fetchone()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1])
    return None

def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, username TEXT, content TEXT, original_filenames TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, file_urls TEXT)''')
    conn.commit()
    conn.close()
init_db()

# Define route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Define route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        try:
            conn = sqlite3.connect('chat.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Error: Username already taken.', 'danger')
    return render_template('register.html')

# Define route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        conn = sqlite3.connect('chat.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user_data = c.fetchone()
        conn.close()

        if user_data:
            user = User(user_data[0], user_data[1])
            login_user(user)
            return redirect(url_for('chatroom'))
        else:
            flash('Login failed. Invalid username or password.', 'danger')

    return render_template('login.html')

# Define route for the chatroom, which requires user login
@app.route('/chatroom')
@login_required
def chatroom():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT username, content, file_urls, original_filenames, timestamp FROM messages ORDER BY timestamp')
    messages = c.fetchall()
    conn.close()

    # Convert timestamp string to datetime object and split file_urls and original_filenames into lists
    processed_messages = []
    for message in messages:
        username, content, file_urls, original_filenames, timestamp = message
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')  # Add this line to convert the timestamp string to a datetime object
        file_urls_list = file_urls.split(',') if file_urls else []
        original_filenames_list = original_filenames.split(',') if original_filenames else []
        processed_messages.append((username, content, file_urls_list, original_filenames_list, timestamp))

    return render_template('chatroom.html', username=current_user.username, messages=processed_messages)

# Define route for user logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Socket.IO event listener for handling incoming messages
@socketio.on('message')
def handle_message(data):
    print(f"Message Data: {data}")

    conn = sqlite3.connect('chat.db')
    c = conn.cursor()

    # Store the file_urls and original_filenames as comma-separated strings in the messages table
    c.execute('INSERT INTO messages (username, content, file_urls, original_filenames) VALUES (?, ?, ?, ?)',
              (data['username'], data['content'], ','.join(data['file_urls']) if 'file_urls' in data else None, ','.join(data['original_filenames']) if 'original_filenames' in data else None))
                
    conn.commit()
    # Get the inserted message's timestamp
    message_id = c.lastrowid
    c.execute('SELECT timestamp FROM messages WHERE id=?', (message_id,))
    message_timestamp = c.fetchone()[0]
    conn.close()

    # Convert the timestamp to a timezone-aware datetime object
    naive_timestamp = datetime.strptime(message_timestamp, '%Y-%m-%d %H:%M:%S')
    aware_timestamp = naive_timestamp.replace(tzinfo=timezone.utc)

    # Add the timestamp to the data sent to the client
    data['timestamp'] = aware_timestamp.isoformat()
    emit('message', data, broadcast=True)



# Define route for handling file uploads
@app.route('/upload_file', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            # Generate a random UUID to prevent filename conflicts
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            return url_for('static', filename=f'uploads/{unique_filename}')

# Define route for serving uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the application with socket.io support
if __name__ == '__main__':
    socketio.run(app, debug=True)
