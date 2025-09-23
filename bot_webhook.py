from flask import Flask, request
from telegram_bot import setup_bot
from config import Config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
application = setup_bot()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука от Telegram"""
    try:
        update = request.get_json()
        application.update_queue.put_nowait(update)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return 'Error', 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Установка вебхука (вызвать один раз)"""
    try:
        webhook_url = f"{Config.APP_URL}/webhook"
        application.bot.set_webhook(webhook_url)
        return f"Webhook set to: {webhook_url}"
    except Exception as e:
        return f"Error setting webhook: {e}"

@app.route('/remove_webhook', methods=['GET'])
def remove_webhook():
    """Удаление вебхука"""
    try:
        application.bot.delete_webhook()
        return "Webhook removed"
    except Exception as e:
        return f"Error removing webhook: {e}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
