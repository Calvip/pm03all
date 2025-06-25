import os
import threading
from dotenv import load_dotenv
import telebot
from flask import Flask, request, jsonify
import json

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('API_KEY')  # Ключ для авторизации API запросов

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# Функция загрузки словаря чатов
def load_user_chats():
    if not os.path.exists('data.json'):
        return {}
    else:
        with open('data.json', 'r') as f:
            return json.load(f)

# Словарь для хранения chat_id пользователей
user_chats = load_user_chats()

# Функция сохранения словаря чатов
def save_user_chats():
    with open('data.json', 'w') as f:
        json.dump(user_chats, f)



# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_chats[user_id] = chat_id
    save_user_chats()
    bot.reply_to(message, f"Вы успешно зарегистрированы! Ваш ID: {user_id}")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.reply_to(message, "Отправьте /start для регистрации")

# API endpoint для отправки уведомлений
@app.route('/send_notification', methods=['POST'])
def send_notification():
    # Проверка API ключа
    if request.headers.get('X-API-KEY') != API_KEY:
        return jsonify({"status": "error", "message": "Invalid API key"}), 403
    
    data = request.json
    user_id = str(data.get('user_id'))
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({"status": "error", "message": "Missing user_id or message"}), 400
    
    if user_id not in user_chats:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    try:
        bot.send_message(chat_id=user_chats[user_id], text=message)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Функция для запуска бота в отдельном потоке
def run_bot():
    print("Бот запущен...")
    # Загружаем список чатов
    load_user_chats()
    bot.infinity_polling()

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Запускаем Flask сервер для API
    app.run(host='0.0.0.0', port=5050)