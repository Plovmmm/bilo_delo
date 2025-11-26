import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv
from web_app import WebApplication
import threading

# Настройка логирования
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )


load_dotenv()

# Токен бота от BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN")
web_app_url = os.getenv("WEB_APP_URL")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    # Замените YOUR_PUBLIC_IP на ваш реальный IP или домен
    
    keyboard = [
        [InlineKeyboardButton("Открыть Mini App", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        "Это твоё личное приложение супер карта АУЕ!!!\n"
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
    app = WebApplication()
    flask_thread = threading.Thread(target=app.run_flask, daemon=True)
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