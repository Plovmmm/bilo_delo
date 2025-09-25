from flask import Flask, send_from_directory
from flask import Flask, render_template, request, jsonify
import threading
from database_manager import DatabaseManager
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import base64


load_dotenv()
YANDEX_MAPS_API_KEY = os.getenv("YANDEX_MAPS_API_KEY")
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
        self.app.add_url_rule('/api/create_mark', 'create_mark', self.create_mark, methods=['POST'])
        self.app.add_url_rule('/api/get_mark/<int:mark_id>', 'get_mark_details', self.get_mark_details, methods=['GET'])

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
    

    def create_user(self, user_telegram_id):
        user_id = self.db_manager.create_user(user_telegram_id)
        return user_id
    

    def get_marks(self, user_telegram_id):
        """GET - получение списка меток"""
        # Находим пользователя
        user = self.db_manager.get_user_by_telegram_id(user_telegram_id)
        if not user:
            user = self.create_user(user_telegram_id=user_telegram_id)
            if not user:
                return jsonify({'error': 'Ошибка при создании пользователя'}), 404
        
        # Получаем метки пользователя
        marks = self.db_manager.get_user_marks(user['id'])
        
        # Добавляем фото к каждой метке
        for mark in marks:
            mark['photos'] = self.db_manager.get_mark_photos_filename(mark['id'])
        
        return jsonify({
            'success': True,
            'marks': marks,
            'user_id': user['id']
        })
    

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    def create_mark(self):
        user_telegram_id = request.form.get('user_telegram_id', None)
        title = request.form.get('title', None)
        description = request.form.get('description', None)
        visit_date = request.form.get('visit_date', None)
        lat = request.form.get('lat', None)
        lon = request.form.get('lon', None)
        address = request.form.get('address', None)

        if not all([user_telegram_id, title, lat, lon]):
            return jsonify({
                'success': False, 
                'message': 'Не заполнены обязательные поля'
            }), 400

        coords = [lat, lon]

        user = self.db_manager.get_user_by_telegram_id(user_telegram_id)
        if not user:
            return jsonify({
                'success': False, 
                'message': 'Пользователь не найден'
            }), 404

        user_id = user.get('id')

        mark = self.db_manager.create_mark(user_id, title, coords, visit_date, description, address)
        if not mark:
            return jsonify({'success': False, 'message': 'Ты хуйню добавил'})
        mark_id = mark.get('id')

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
                photo = self.db_manager.add_photo(mark_id=mark_id, filename=filename, is_main=True)

        if 'secondary_photos' in request.files:
            photos = request.files.getlist('secondary_photos')
            for index, file in enumerate(photos):
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
                    photo = self.db_manager.add_photo(mark_id=mark_id, filename=filename, is_main=False)
                
        return jsonify({
            'success': True, 
            'mark': {
                'id': mark_id,
                'title': title,
                'address': address,
                'visit_date': visit_date,
                'description': description,
                'coords': coords
            }
        })
    

    def get_mark_details(self, mark_id):
        """Получение полной информации о метке"""
        try:
            # Получаем метку из БД
            mark = self.db_manager.get_mark_by_id(mark_id)
            if not mark:
                return jsonify({'success': False, 'message': 'Место не найдено'}), 404
            

            main_photo = self.db_manager.get_main_photo_filename(mark_id)
            # Получаем фото метки
            photos = self.db_manager.get_mark_photos_filename(mark_id)
            
            # Форматируем ответ

            mark_data = {
                'title': mark.get('title'),
                'description': mark.get('description', ''),
                'visit_date': mark.get('visit_date').strftime('%Y-%m-%d'),
                'address': mark.get('address')
            }
            
            if main_photo:
                file_path = os.path.join(UPLOAD_FOLDER, main_photo[0])
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        image_data = f.read()

                        base64_image = base64.b64encode(image_data).decode('utf-8')
                        mark_data["main_photo"] = f"data:image/jpeg;base64,{base64_image}"
            
            

            if photos:
                for photo in photos:
                    mark_data["photos"] = []
                    file_path = os.path.join(UPLOAD_FOLDER, photo.get('filename'))
                    if os.path.isfile(file_path):
                        with open(file_path, 'rb') as f:
                            image_data = f.read()
                            base64_image = base64.b64encode(image_data).decode('utf-8')
                            mark_data["photos"].append(f"data:image/jpeg;base64,{base64_image}")
            return jsonify({'success': True, 'mark': mark_data})
            
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500


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
