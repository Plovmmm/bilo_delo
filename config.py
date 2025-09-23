import os

class Config:
    # Telegram Bot API
    BOT_TOKEN = "8441513229:AAGc7tuq_6f8lh5Rxfg1aAZ50H48yGJ8Ql4"
    ADMIN_ID = "ваш_telegram_id"  # Заменим на ваш реальный ID
    
    # Яндекс.Карты API
    YANDEX_MAPS_API_KEY = "ваш_ключ_яндекс_карт"  # Получим бесплатно
    
    # Настройки приложения
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'bilo_delo.db'
