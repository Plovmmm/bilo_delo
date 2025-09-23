from flask import Flask, render_template, request, jsonify, session
import sqlite3
import json
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(Config.DATABASE_URL)
    c = conn.cursor()
    
    # Таблица пользователей (для будущего расширения)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  telegram_id TEXT UNIQUE NOT NULL,
                  username TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Таблица мест (основная)
    c.execute('''CREATE TABLE IF NOT EXISTS places
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT NOT NULL,
                  title TEXT NOT NULL,
                  description TEXT,
                  address TEXT,
                  lat REAL NOT NULL,
                  lon REAL NOT NULL,
                  date_visited DATE DEFAULT CURRENT_DATE,
                  main_photo TEXT,
                  photos TEXT DEFAULT '[]',
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Добавляем админа если его нет
    try:
        c.execute("INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (Config.ADMIN_ID,))
        conn.commit()
    except:
        pass
    
    conn.close()

@app.route('/')
def index():
    """Главная страница для админа"""
    return render_template('index.html', 
                         yandex_maps_key=Config.YANDEX_MAPS_API_KEY,
                         user_id=Config.ADMIN_ID,
                         is_admin=True)

@app.route('/guest/<user_id>')
def guest_map(user_id):
    """Карта для гостя по ссылке"""
    return render_template('guest_map.html',
                         yandex_maps_key=Config.YANDEX_MAPS_API_KEY,
                         user_id=user_id,
                         is_admin=False)

# API endpoints
@app.route('/api/places', methods=['GET'])
def get_places():
    """Получить все метки пользователя"""
    user_id = request.args.get('user_id')
    conn = sqlite3.connect(Config.DATABASE_URL)
    c = conn.cursor()
    c.execute("SELECT * FROM places WHERE user_id = ? ORDER BY date_visited DESC", (user_id,))
    places = c.fetchall()
    conn.close()
    
    # Преобразуем в JSON формат
    result = []
    for place in places:
        result.append({
            'id': place[0],
            'title': place[2],
            'description': place[3] or '',
            'address': place[4] or '',
            'lat': place[5],
            'lon': place[6],
            'date_visited': place[7],
            'main_photo': place[8] or '',
            'photos': json.loads(place[9]) if place[9] else []
        })
    
    return jsonify(result)

@app.route('/api/places', methods=['POST'])
def add_place():
    """Добавить новую метку"""
    try:
        data = request.json
        conn = sqlite3.connect(Config.DATABASE_URL)
        c = conn.cursor()
        
        c.execute('''INSERT INTO places 
                     (user_id, title, description, address, lat, lon, date_visited, main_photo, photos)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['user_id'], data['title'], data.get('description', ''),
                   data.get('address', ''), data['lat'], data['lon'],
                   data.get('date_visited', datetime.now().date().isoformat()),
                   data.get('main_photo', ''), data.get('photos', '[]')))
        
        conn.commit()
        place_id = c.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': place_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/places/<int:place_id>', methods=['PUT'])
def update_place(place_id):
    """Обновить метку"""
    try:
        data = request.json
        conn = sqlite3.connect(Config.DATABASE_URL)
        c = conn.cursor()
        
        c.execute('''UPDATE places SET 
                     title=?, description=?, address=?, date_visited=?, 
                     main_photo=?, photos=?
                     WHERE id=? AND user_id=?''',
                  (data['title'], data.get('description', ''), data.get('address', ''),
                   data.get('date_visited'), data.get('main_photo', ''),
                   data.get('photos', '[]'), place_id, data['user_id']))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/places/<int:place_id>', methods=['DELETE'])
def delete_place(place_id):
    """Удалить метку"""
    try:
        user_id = request.args.get('user_id')
        conn = sqlite3.connect(Config.DATABASE_URL)
        c = conn.cursor()
        
        c.execute("DELETE FROM places WHERE id=? AND user_id=?", (place_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
