import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import Config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = str(update.effective_user.id)
    
    # Проверяем является ли пользователь админом
    if user_id == Config.ADMIN_ID:
        # Создаем клавиатуру с кнопкой открытия мини-приложения
        keyboard = [
            [InlineKeyboardButton("🗺️ Открыть карту", web_app={'url': 'https://cj33147.tw1.ru/'})],
            [InlineKeyboardButton("🔗 Поделиться картой", callback_data='share_map')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(
            f"Привет! Это твое мини-приложение 'Было дело'.\n"
            f"Твой ID: {user_id}\n\n"
            f"Нажми кнопку ниже чтобы открыть карту:",
            reply_markup=reply_markup
        )
    else:
        # Для гостей - отправляем сообщение что доступ только у админа
        await update.message.reply_html(
            "👋 Привет! Это мини-приложение 'Было дело'.\n"
            "Сейчас доступ в режиме разработки. Скоро здесь можно будет просматривать карты друзей!"
        )

async def share_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация ссылки для общего доступа"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    if user_id == Config.ADMIN_ID:
        share_url = f"https://cj33147.tw1.ru/guest/{user_id}"
        await query.edit_message_text(
            f"🔗 Ссылка для доступа к твоей карте:\n\n"
            f"{share_url}\n\n"
            f"Отправь эту ссылку друзьям, чтобы они могли посмотреть твою карту!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🗺️ Открыть карту", url=share_url)]])
        )

def setup_bot():
    """Настройка и запуск бота"""
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(share_map, pattern='share_map'))
    
    return application
