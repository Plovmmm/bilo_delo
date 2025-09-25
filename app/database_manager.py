import psycopg2 # type: ignore
from psycopg2 import pool # type: ignore
import os
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.connection_pool = None

    def _execute_query(self, query, params=None):
        """Универсальный метод для выполнения SQL запросов"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                
                # Для SELECT запросов возвращаем результаты
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                # Для INSERT с RETURNING возвращаем одну запись
                elif query.strip().upper().startswith('INSERT'):
                    conn.commit()
                    return cursor.fetchone() if cursor.description else None
                # Для UPDATE/DELETE возвращаем количество затронутых строк
                else:
                    conn.commit()
                    return cursor.rowcount
                
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Ошибка выполнения запроса: {e}")
            raise e
        finally:
            self.return_connection(conn)
        
    def init_pool(self, min_conn=1, max_conn=10):
        """Инициализация connection pool"""
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=min_conn,
                maxconn=max_conn,
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'bilodelo'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                port=os.getenv('DB_PORT', '5432')
            )
            print("✅ Connection pool инициализирован")
            return True
        except Exception as e:
            print(f"❌ Ошибка инициализации pool: {e}")
            return False
    
    def get_connection(self):
        """Получение соединения из pool"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None
    
    def return_connection(self, conn):
        """Возврат соединения в pool"""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)
    
    def create_tables(self):
        """Создание всех таблиц"""
        try:
            conn = self.get_connection()
            if not conn:
                raise Exception("Не удалось получить соединение")
            
            with conn.cursor() as cursor:
                # Таблица пользователей
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Таблица меток (marks)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS marks (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        title VARCHAR(200) NOT NULL,
                        description TEXT,
                        visit_date DATE NOT NULL,
                        address TEXT,
                        lat DECIMAL(10, 8) NOT NULL,
                        lon DECIMAL(11, 8) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        
                        CONSTRAINT valid_coordinates CHECK (
                            lat BETWEEN -90 AND 90 AND 
                            lon BETWEEN -180 AND 180
                        )
                    );
                """)
                
                # Таблица фотографий
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS photos (
                        id SERIAL PRIMARY KEY,
                        mark_id INTEGER NOT NULL REFERENCES marks(id) ON DELETE CASCADE,
                        filename VARCHAR(255) NOT NULL,
                        is_main BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                conn.commit()
                print("✅ Таблицы созданы успешно")
                
        except Exception as e:
            print(f"❌ Ошибка создания таблиц: {e}")
            if conn:
                conn.rollback()
        finally:
            self.return_connection(conn)
    
    def create_indexes(self):
        """Создание индексов для оптимизации"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);",
                    "CREATE INDEX IF NOT EXISTS idx_marks_user_id ON marks(user_id);",
                    "CREATE INDEX IF NOT EXISTS idx_marks_coordinates ON marks(lat, lon);",
                    "CREATE INDEX IF NOT EXISTS idx_photos_mark_id ON photos(mark_id);",
                    "CREATE INDEX IF NOT EXISTS idx_photos_is_main ON photos(is_main);"
                ]
                
                for index_query in indexes:
                    cursor.execute(index_query)
                
                conn.commit()
                print("✅ Индексы созданы успешно")
                
        except Exception as e:
            print(f"❌ Ошибка создания индексов: {e}")
            if conn:
                conn.rollback()
        finally:
            self.return_connection(conn)

    # DAO МЕТОДЫ ДЛЯ ПОЛЬЗОВАТЕЛЕЙ
    def create_user(self, telegram_id):
        """Создание нового пользователя"""
        query = """
        INSERT INTO users (telegram_id) 
        VALUES (%s) 
        ON CONFLICT (telegram_id) DO NOTHING
        RETURNING id;
        """
        result = self._execute_query(query, (telegram_id,))
        if result:
            return {
                "id": result[0]
            }
        return None
    
    def get_user_by_telegram_id(self, telegram_id):
        """Получение пользователя по Telegram ID"""
        query = """
        SELECT id, telegram_id, created_at 
        FROM users 
        WHERE telegram_id = %s;
        """
        result = self._execute_query(query, (telegram_id,))
        if result:
            return {
                "id": result[0][0],
                "telegram_id": result[0][1],
                "created_at": result[0][2]
            }
        return None
    
    # DAO МЕТОДЫ ДЛЯ МЕТОК
    def create_mark(self, user_id, title, coords, visit_date=None, description=None, address=None):
        """Создание новой метки"""
        query = """
        INSERT INTO marks 
        (user_id, title, description, visit_date, address, lat, lon) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = self._execute_query(query, (user_id, title, description, visit_date, address, coords[0], coords[1]))
        if result:
            return {
                "id": result[0]
            }
        return None
    
    def get_user_marks(self, user_id):
        """Получение всех меток пользователя"""
        query = """
        SELECT id, user_id, title, description, visit_date, address, lat, lon, created_at
        FROM marks 
        WHERE user_id = %s
        ORDER BY visit_date DESC, created_at DESC;
        """
        result = self._execute_query(query, (user_id,))
        if result:
            marks = []
            for mark in result:
                marks.append({
                    "id": mark[0],
                    "user_id": mark[1],
                    "title": mark[2],
                    "description": mark[3],
                    "visit_date": mark[4],
                    "address": mark[5],
                    "lat": mark[6],
                    "lon": mark[7],
                    "created_at": mark[8]
                })
            return marks
        return []
    
    def get_user_marks_coords(self, user_id):
        """Получение всех координат меток пользователя"""
        query = """
        SELECT id, lat, lon, user_id
        FROM marks 
        WHERE user_id = %s
        ORDER BY visit_date DESC, created_at DESC;
        """
        result = self._execute_query(query, (user_id,))
        if result:
            marks = []
            for mark in result:
                marks.append({
                    "id": mark[0],
                    "lat": mark[1],
                    "lon": mark[2],
                    "user_id": mark[3]
                })
            return marks
        return []
    
    
    def get_mark_by_id(self, mark_id):
        """Получение метки по ID"""
        query = """
        SELECT id, user_id, title, description, visit_date, address, lat, lon, created_at
        FROM marks 
        WHERE id = %s;
        """
        result = self._execute_query(query, (mark_id,))
        if result:
            return {
                "id": result[0][0],
                "user_id": result[0][1],
                "title": result[0][2],
                "description": result[0][3],
                "visit_date": result[0][4],
                "address": result[0][5],
                "lan": result[0][6],
                "log": result[0][7],
                "created_at": result[0][8]
            }
        return None
    
    def delete_mark(self, mark_id, user_id):
        """Удаление метки"""
        query = "DELETE FROM marks WHERE id = %s AND user_id = %s;"
        return self._execute_query(query, (mark_id, user_id))
    
    def update_mark(self, mark_id, user_id, **kwargs):
        """Обновление метки"""
        if not kwargs:
            return 0
        
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        query = f"UPDATE marks SET {set_clause} WHERE id = %s AND user_id = %s;"
        params = list(kwargs.values()) + [mark_id, user_id]
        return self._execute_query(query, params)
    
    # DAO МЕТОДЫ ДЛЯ ФОТОГРАФИЙ
    def add_photo(self, mark_id, filename, is_main=False):
        """Добавление фотографии к метке"""
        # Если это главное фото, снимаем флаг с предыдущего
        if is_main:
            self._execute_query(
                "UPDATE photos SET is_main = FALSE WHERE mark_id = %s AND is_main = TRUE;",
                (mark_id,)
            )
        
        query = """
        INSERT INTO photos (mark_id, filename, is_main) 
        VALUES (%s, %s, %s)
        RETURNING id, mark_id, filename, is_main, created_at;
        """
        result = self._execute_query(query, (mark_id, filename, is_main))
        if result:
            return {
                'id': result[0],
                'mark_id': result[1],
                'filename': result[2],
                'is_main': result[3],
            }
        return None
    
    def get_mark_photos_filename(self, mark_id):
        """Получение всех фотографий метки"""
        query = """
        SELECT filename 
        FROM photos 
        WHERE mark_id = %s AND is_main = FALSE
        ORDER BY is_main DESC, created_at ASC;
        """
        result = self._execute_query(query, (mark_id,))
        if result:
            return [{"filename": photo_data[0]} for photo_data in result]
        return []
    
    def get_main_photo_filename(self, mark_id):
        """Получение главной фотографии метки"""
        query = """
        SELECT filename
        FROM photos 
        WHERE mark_id = %s AND is_main = TRUE 
        LIMIT 1;
        """
        result = self._execute_query(query, (mark_id,))
        if result:
            return result[0]
        return None
    
    def delete_photo(self, photo_id):
        """Удаление фотографии"""
        query = "DELETE FROM photos WHERE id = %s;"
        return self._execute_query(query, (photo_id,))
    
    def update_photo_as_main(self, photo_id, mark_id):
        """Установка фотографии как главной"""
        # Сначала снимаем флаг со всех фото места
        self._execute_query(
            "UPDATE photos SET is_main = FALSE WHERE mark_id = %s;",
            (mark_id,)
        )
        # Затем устанавливаем новое главное фото
        query = "UPDATE photos SET is_main = TRUE WHERE id = %s AND mark_id = %s;"
        return self._execute_query(query, (photo_id, mark_id))

    # УТИЛИТНЫЕ МЕТОДЫ
    def get_user_with_marks_coords(self, telegram_id):
        """Получение пользователя со всеми его метками и фото"""
        user = self.get_user_by_telegram_id(telegram_id)
        if not user:
            return None
        
        marks = self.get_user_marks(user[0])  # user[0] - id пользователя
        result_user = {
            'id': user[0],
            'telegram_id': user[1],
            'created_at': user[2],
            'marks': []
        }
        
        for mark in marks:
            mark_dict = {
                'id': mark[0],
                'x': float(mark[6]),
                'y': float(mark[7])
            }
            result_user['marks'].append(mark_dict)
        
        return result_user


if __name__ == "__main__":
    # Глобальный экземпляр DatabaseManager
    db_manager = DatabaseManager()

    def init_database():
        """Инициализация базы данных"""
        if db_manager.init_pool():
            db_manager.create_tables()
            db_manager.create_indexes()
            return True
        return False