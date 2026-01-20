from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'securetrack2026'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id=1, username='admin'):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    return User(id=int(user_id))

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            user = User()
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next', url_for('track'))
            return redirect(next_page)
        flash('Use: admin/admin123', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    conn = get_db_connection()
    if request.method == 'POST':
        tracking_id = request.form['tracking_id']
        sender = request.form['sender']
        receiver = request.form['receiver']
        conn.execute('INSERT INTO couriers (tracking_id, sender, receiver) VALUES (?, ?, ?)',
                    (tracking_id, sender, receiver))
        conn.commit()
        flash('New courier added!')
    conn.close()
    return render_template('admin.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
def track():
    conn = get_db_connection()
    if request.method == 'POST':
        tracking_id = request.form['tracking_id']
        courier = conn.execute('SELECT * FROM couriers WHERE tracking_id = ?', (tracking_id,)).fetchone()
        if courier:
            locations = conn.execute('SELECT * FROM locations WHERE courier_id = ? ORDER BY timestamp DESC', (courier['id'],)).fetchall()
        else:
            locations = []
            flash('Tracking ID not found')
        conn.close()
        return render_template('track.html', courier=courier, locations=locations)
    couriers = conn.execute('SELECT * FROM couriers').fetchall()
    conn.close()
    return render_template('index.html', couriers=couriers)

@app.route('/update_gps/<tracking_id>')
@login_required
def update_gps(tracking_id):
    conn = get_db_connection()
    courier = conn.execute('SELECT * FROM couriers WHERE tracking_id = ?', (tracking_id,)).fetchone()
    if courier:
        lat = 17.3850 + random.uniform(-0.1, 0.1)
        lng = 78.4867 + random.uniform(0, 1.0)
        conn.execute('INSERT INTO locations (courier_id, latitude, longitude) VALUES (?, ?, ?)',
                    (courier['id'], lat, lng))
        conn.commit()
        flash('GPS location updated!')
    conn.close()
    return redirect(url_for('track'))

if __name__ == '__main__':
    app.run(debug=True)
