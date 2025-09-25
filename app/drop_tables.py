import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

class TableDropper:
    def __init__(self):
        self.connection_pool = None
        
    def init_pool(self):
        """Инициализация connection pool"""
        try:
            self.connection_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=5,
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
    
    def _execute_query(self, query):
        """Выполнение SQL запроса"""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            conn.rollback()
            return False
        finally:
            self.connection_pool.putconn(conn)
    
    def drop_photos_table(self):
        """Удаление таблицы photos"""
        try:
            query = "DROP TABLE IF EXISTS photos CASCADE;"
            success = self._execute_query(query)
            if success:
                print("✅ Таблица photos удалена")
            return success
        except Exception as e:
            print(f"❌ Ошибка при удалении таблицы photos: {e}")
            return False
    
    def drop_marks_table(self):
        """Удаление таблицы marks"""
        try:
            query = "DROP TABLE IF EXISTS marks CASCADE;"
            success = self._execute_query(query)
            if success:
                print("✅ Таблица marks удалена")
            return success
        except Exception as e:
            print(f"❌ Ошибка при удалении таблицы marks: {e}")
            return False
    
    def drop_users_table(self):
        """Удаление таблицы users"""
        try:
            query = "DROP TABLE IF EXISTS users CASCADE;"
            success = self._execute_query(query)
            if success:
                print("✅ Таблица users удалена")
            return success
        except Exception as e:
            print(f"❌ Ошибка при удалении таблицы users: {e}")
            return False
    
    def drop_all_tables(self):
        """Удаление всех таблиц в правильном порядке"""
        print("🗑️  Начинаем удаление таблиц...")
        
        # Порядок важен: сначала дочерние таблицы, потом родительские
        success_photos = self.drop_photos_table()
        success_marks = self.drop_marks_table() 
        success_users = self.drop_users_table()
        
        all_success = success_photos and success_marks and success_users
        
        if all_success:
            print("🎉 Все таблицы успешно удалены!")
        else:
            print("⚠️  Некоторые таблицы не были удалены")
        
        return all_success
    
    def check_tables_exist(self):
        """Проверка существования таблиц перед удалением"""
        conn = self.connection_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('users', 'marks', 'photos');
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]
                return existing_tables
        finally:
            self.connection_pool.putconn(conn)
    
    def close_pool(self):
        """Закрытие connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✅ Connection pool закрыт")


def main():
    """Основная функция"""
    dropper = TableDropper()
    
    if not dropper.init_pool():
        return
    
    try:
        # Проверяем какие таблицы существуют
        existing_tables = dropper.check_tables_exist()
        if existing_tables:
            print(f"📋 Найдены таблицы: {', '.join(existing_tables)}")
        else:
            print("📋 Таблицы не найдены")
        
        # Подтверждение удаления
        confirmation = input("❓ Вы уверены что хотите удалить все таблицы? (y/N): ")
        if confirmation.lower() != 'y':
            print("❌ Удаление отменено")
            return
        
        # Удаляем таблицы
        dropper.drop_all_tables()
        
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
    finally:
        dropper.close_pool()


if __name__ == "__main__":
    main()