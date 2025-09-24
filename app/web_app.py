from flask import Flask, send_from_directory
from flask import Flask, render_template, request, jsonify
import threading
from database_manager import DatabaseManager
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename


load_dotenv()
YANDEX_MAPS_API_KEY = os.getenv("YANDEX_MAPS_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
UPLOAD_FOLDER = "upload"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heif', 'bmp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class WebApplication:
    def __init__(self):
        self.app = Flask(__name__,
            template_folder='templates',
            static_folder='static'
        )
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/api/get_marks/<int:user_telegram_id>', 'get_marks', self.get_marks, methods=['GET'])
        self.app.add_url_rule('/create_mark', 'create_mark', self.create_mark, methods=['POST'])

        self.db_manager = DatabaseManager()
        self.init_database()


    def init_database(self):
        """Инициализация базы данных"""
        if self.db_manager.init_pool():
            self.db_manager.create_tables()
            self.db_manager.create_indexes()
            return True
        return False


    def index(self):
        """Главная страница мини-приложения"""
        return render_template('index.html', is_admin=True, yandex_maps_key=YANDEX_MAPS_API_KEY)
    

    def get_marks(self, user_telegram_id):
        """GET - получение списка меток"""
        # Находим пользователя
        user = self.db_manager.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Получаем метки пользователя
        marks = self.db_manager.get_user_marks(user['id'])
        
        # Добавляем фото к каждой метке
        for mark in marks:
            mark['photos'] = self.db_manager.get_mark_photos(mark['id'])
        
        return jsonify({
            'success': True,
            'marks': marks,
            'user_id': user['id']
        })
    

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    def create_mark(self):
        if 'user_telegram_id' not in request.files:
            return jsonify({'success': False, 'message': 'user_telegram_id не найден'})
        if 'name' not in request.files:
            return jsonify({'success': False, 'message': 'Название метки не найдено'})
        if 'coords' not in request.files:
            return jsonify({'success': False, 'message': 'Координаты метки не найдены'})

        user_telegram_id = request.files['user_telegram_id']
        name = request.files['name']
        coords = request.files['coords']
        visit_date = request.files.get('visit_date', None)
        description = request.files.get('description', None)
        address = request.files.get('address', None)

        user = self.db_manager.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return jsonify({'success': False, 'message': 'Пользователь не найден'})

        user_id = user[0]

        mark_id = self.db_manager.create_mark(user_id, name, coords, visit_date, description, address)

        if 'main_photo' in request.files:
            file = request.files['main_photo']
            # Проверяем тип файла
            if file and self.allowed_file(file.filename):
                # Безопасное имя файла
                filename = secure_filename(file.filename)
                # Добавляем timestamp к имени файла для уникальности
                import time
                timestamp = str(int(time.time()))
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{timestamp}{ext}"

                # Сохраняем файл
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                self.db_manager.add_photo(mark_id=mark_id, filename=filename, is_main=True)


        if 'photos' in request.files:
            photos = request.files['photos']
            for photo in enumerate(photos):
                index = photo[0]
                file = photo[1]
                # Проверяем тип файла
                if file and self.allowed_file(file.filename):
                    # Безопасное имя файла
                    filename = secure_filename(file.filename)
                    # Добавляем timestamp к имени файла для уникальности
                    import time
                    timestamp = str(int(time.time()))
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{timestamp}_{index}{ext}"

                    # Сохраняем файл
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    self.db_manager.add_photo(mark_id=mark_id, filename=filename, is_main=False)
                
            return jsonify({
                'success': True, 
                'message': 'Файл успешно загружен',
                'filename': filename
            })
        
        return jsonify({'success': False, 'message': 'Недопустимый тип файла'})


    def run_flask(self):
        """Запуск Flask сервера"""
        self.app.run(host='0.0.0.0', port=5000, debug=False)


    def startFlask(self, daemon):
        if daemon:
            flask_thread = threading.Thread(target=self.run_flask, daemon=daemon)
            flask_thread.start()
        else:
            self.run_flask()


if __name__ == '__main__':
    app = WebApplication()
    app.startFlask(False)
