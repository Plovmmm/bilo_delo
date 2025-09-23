import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, send_from_directory
from flask import Flask, render_template, request, jsonify
import threading
import os
from dotenv import load_dotenv

# Настройка логирования
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )


load_dotenv()

# Токен бота от BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")
web_app_url = os.getenv("WEB_APP_URL")

# Создаем Flask приложение для сервера статических файлов
app = Flask(__name__,
    template_folder='templates',
    static_folder='static'
)


@app.route('/')
def index():
    """Главная страница мини-приложения"""
    return render_template('index.html', is_admin=True)


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)


def run_flask():
    """Запуск Flask сервера"""
    app.run(host='0.0.0.0', port=5000, debug=False)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    # Замените YOUR_PUBLIC_IP на ваш реальный IP или домен
    
    keyboard = [
        [InlineKeyboardButton("Открыть Mini App", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        "Привет! Это демо Mini App.\n\n"
        "Нажми кнопку ниже чтобы открыть приложение:",
        reply_markup=reply_markup
    )


async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка данных из Mini App"""
    try:
        if update.message and update.message.web_app_data:
            data = update.message.web_app_data.data
            await update.message.reply_text(f"Получены данные из Mini App: {data}")
    except Exception as e:
        logging.error(f"Error processing web app data: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logging.error(f"Exception while handling an update: {context.error}")


def main():
    """Основная функция"""
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(web_app_data_handler))
    
    # Запускаем бота
    print("Бот запущен! Flask сервер работает на порту 5000")
    application.run_polling()


if __name__ == '__main__':
    main()