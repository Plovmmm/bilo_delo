from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# ID админа (ваш)
ADMIN_ID = "ваш_telegram_id"  # Заменим на ваш реальный ID

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('bilo_delo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS places
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT NOT NULL,
                  title TEXT NOT NULL,
                  description TEXT,
                  address TEXT,
                  lat REAL NOT NULL,
                  lon REAL NOT NULL,
                  date_visited DATE,
                  main_photo TEXT,
                  photos TEXT,  # JSON список дополнительных фото
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Главная страница мини-приложения"""
    return render_template('index.html')

@app.route('/guest/<user_id>')
def guest_map(user_id):
    """Карта для гостя по ссылке"""
    return render_template('guest_map.html', user_id=user_id)

# API endpoints
@app.route('/api/places', methods=['GET'])
def get_places():
    """Получить все метки пользователя"""
    user_id = request.args.get('user_id')
    conn = sqlite3.connect('bilo_delo.db')
    c = conn.cursor()
    c.execute("SELECT * FROM places WHERE user_id = ?", (user_id,))
    places = c.fetchall()
    conn.close()
    
    # Преобразуем в JSON формат
    result = []
    for place in places:
        result.append({
            'id': place[0],
            'title': place[2],
            'description': place[3],
            'address': place[4],
            'lat': place[5],
            'lon': place[6],
            'date_visited': place[7],
            'main_photo': place[8],
            'photos': place[9] if place[9] else '[]'
        })
    
    return jsonify(result)

@app.route('/api/places', methods=['POST'])
def add_place():
    """Добавить новую метку"""
    data = request.json
    conn = sqlite3.connect('bilo_delo.db')
    c = conn.cursor()
    c.execute('''INSERT INTO places 
                 (user_id, title, description, address, lat, lon, date_visited, main_photo, photos)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['user_id'], data['title'], data['description'], 
               data['address'], data['lat'], data['lon'],
               data['date_visited'], data['main_photo'], data['photos']))
    conn.commit()
    place_id = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': place_id})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
