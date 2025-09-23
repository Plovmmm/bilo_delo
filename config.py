import os

class Config:
    # Telegram Bot API
    BOT_TOKEN = "8441513229:AAGc7tuq_6f8lh5Rxfg1aAZ50H48yGJ8Ql4"
    ADMIN_ID = "1323961884"  # Ваш реальный Telegram ID
    
    # Яндекс.Карты API
    YANDEX_MAPS_API_KEY = "e3ae341e-a8e0-4284-8d2f-cc20984dc27e"
    
    # Настройки приложения
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bilo-delo-secret-key-2024'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'bilo_delo.db'
    
    # URL приложения
    APP_URL = "https://cj33147.tw1.ru"
