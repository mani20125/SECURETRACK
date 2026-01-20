from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'securetrack2026'
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'])
    return None

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, password TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS couriers (id INTEGER PRIMARY KEY, user_id INTEGER, tracking_id TEXT UNIQUE, sender TEXT, receiver TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS locations (id INTEGER PRIMARY KEY, courier_id INTEGER, latitude REAL, longitude REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                        (username, email, hashed_password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'danger')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            logged_user = User(user['id'], user['username'], user['email'])
            login_user(logged_user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next', url_for('track'))
            return redirect(next_page)
        flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    conn = get_db_connection()
    user_couriers = conn.execute('SELECT * FROM couriers WHERE user_id = ?', (current_user.id,)).fetchall()
    
    if request.method == 'POST':
        tracking_id = request.form['tracking_id']
        sender = request.form['sender']
        receiver = request.form['receiver']
        conn.execute('INSERT INTO couriers (user_id, tracking_id, sender, receiver) VALUES (?, ?, ?, ?)',
                    (current_user.id, tracking_id, sender, receiver))
        conn.commit()
        flash('New courier added!')
        return redirect(url_for('admin'))
    
    conn.close()
    return render_template('admin.html', couriers=user_couriers)

@app.route('/', methods=['GET', 'POST'])
@login_required
def track():
    conn = get_db_connection()
    if request.method == 'POST':
        tracking_id = request.form['tracking_id']
        courier = conn.execute('SELECT * FROM couriers WHERE user_id = ? AND tracking_id = ?', 
                             (current_user.id, tracking_id)).fetchone()
        if courier:
            locations = conn.execute('SELECT * FROM locations WHERE courier_id = ? ORDER BY timestamp DESC', 
                                   (courier['id'],)).fetchall()
        else:
            locations = []
            flash('Tracking ID not found!')
        conn.close()
        return render_template('track.html', courier=courier, locations=locations)
    
    user_couriers = conn.execute('SELECT * FROM couriers WHERE user_id = ?', (current_user.id,)).fetchall()
    conn.close()
    return render_template('index.html', couriers=user_couriers)

@app.route('/update_gps/<tracking_id>')
@login_required
def update_gps(tracking_id):
    conn = get_db_connection()
    courier = conn.execute('SELECT * FROM couriers WHERE user_id = ? AND tracking_id = ?', 
                          (current_user.id, tracking_id)).fetchone()
    if courier:
        lat = 17.3850 + random.uniform(-0.1, 0.1)  # Hyderabad→Bangalore
        lng = 78.4867 + random.uniform(0, 1.0)
        conn.execute('INSERT INTO locations (courier_id, latitude, longitude) VALUES (?, ?, ?)',
                    (courier['id'], lat, lng))
        conn.commit()
        flash('GPS location updated!')
    conn.close()
    return redirect(url_for('track'))

if __name__ == '__main__':
    app.run()

