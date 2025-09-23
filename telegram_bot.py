import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = str(update.effective_user.id)
    
    if user_id == Config.ADMIN_ID:
        # Ссылка на мини-приложение
        web_app_url = Config.APP_URL
        share_url = f"{Config.APP_URL}/guest/{user_id}"
        
        keyboard = [
            [InlineKeyboardButton("🗺️ Открыть мою карту", web_app={'url': web_app_url})],
            [InlineKeyboardButton("🔗 Поделиться картой", callback_data='share_map')],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_html(
            f"🎉 <b>Добро пожаловать в 'Было дело'!</b>\n\n"
            f"Твой персональный дневник путешествий и посещенных мест.\n\n"
            f"<b>Твой ID:</b> {user_id}\n"
            f"<b>Статус:</b> 👑 Администратор\n\n"
            f"Нажми кнопку ниже чтобы открыть карту:",
            reply_markup=reply_markup
        )
    else:
        # Для гостей
        await update.message.reply_html(
            "👋 <b>Привет!</b>\n\n"
            "Это мини-приложение <b>'Было дело'</b> - дневник посещенных мест.\n\n"
            "Сейчас приложение в режиме разработки. "
            "Скоро здесь можно будет просматривать карты друзей!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📱 Открыть приложение", web_app={'url': Config.APP_URL})
            ]])
        )

async def share_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерация ссылки для общего доступа"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    if user_id == Config.ADMIN_ID:
        share_url = f"{Config.APP_URL}/guest/{user_id}"
        
        keyboard = [
            [InlineKeyboardButton("🗺️ Открыть карту", url=share_url)],
            [InlineKeyboardButton("↩️ Назад", callback_data='back_to_main')]
        ]
        
        await query.edit_message_text(
            f"🔗 <b>Ссылка для общего доступа</b>\n\n"
            f"Отправь эту ссылку друзьям, чтобы они могли посмотреть твою карту:\n\n"
            f"<code>{share_url}</code>\n\n"
            f"Карта откроется в режиме просмотра (без возможности редактирования).",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь по использованию"""
    query = update.callback_query
    await query.answer()
    
    help_text = (
        "ℹ️ <b>Помощь по использованию</b>\n\n"
        "🎯 <b>Как добавить место:</b>\n"
        "1. Нажми '➕ Добавить место'\n"
        "2. Кликни на карте в нужное место\n"
        "3. Заполни информацию о месте\n"
        "4. Сохрани\n\n"
        "🔗 <b>Как поделиться картой:</b>\n"
        "1. Нажми '🔗 Поделиться'\n"
        "2. Отправь ссылку друзьям\n\n"
        "✏️ <b>Редактирование:</b>\n"
        "Кликни на любую метку на карте для просмотра и редактирования"
    )
    
    keyboard = [[InlineKeyboardButton("↩️ Назад", callback_data='back_to_main')]]
    await query.edit_message_text(help_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возврат в главное меню"""
    query = update.callback_query
    await query.answer()
    await start(update, context)  # Переиспользуем логику старта

def setup_bot():
    """Настройка и запуск бота"""
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(share_map, pattern='share_map'))
    application.add_handler(CallbackQueryHandler(help_command, pattern='help'))
    application.add_handler(CallbackQueryHandler(back_to_main, pattern='back_to_main'))
    
    return application
