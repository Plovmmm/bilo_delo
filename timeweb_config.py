"""
Конфигурация для деплоя на Timeweb
"""

# Настройки для Timeweb
TIMEWEB_CONFIG = {
    'python_version': '3.9',
    'requirements': [
        'Flask==2.3.3',
        'python-telegram-bot==20.7', 
        'requests==2.31.0',
        'gunicorn==21.2.0'
    ],
    'start_command': 'gunicorn --bind 0.0.0.0:5000 wsgi:app',
    'environment_variables': {
        'SECRET_KEY': 'bilo-delo-secret-key-2024',
        'ADMIN_ID': '1323961884'
    }
}
