import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import threading
from flask import Flask

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "I'm alive!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask, daemon=True).start()


# Укажите ваш токен бота и Telegram ID администратора
TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_ID = 5084880209  # Замените на ваш Telegram ID

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Клавиатура для отзывов
keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton("Оставить отзыв")]],
    resize_keyboard=True
)

# Команда /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Добро пожаловать в наш ресторан! Пожалуйста, оставьте свой отзыв.", 
        reply_markup=keyboard
    )

# Обработка кнопки "Оставить отзыв"
async def ask_feedback(update: Update, context: CallbackContext):
    if update.message.text == "Оставить отзыв":
        await update.message.reply_text("Напишите ваш отзыв о нашем ресторане:")

# Обработка текстовых сообщений (отзывы)
async def handle_feedback(update: Update, context: CallbackContext):
    user = update.message.from_user
    feedback_text = f"Новый отзыв от @{user.username or user.full_name} ({user.id}):\n{update.message.text}"

    # Отправляем отзыв администратору
    await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_text)

    # Подтверждаем получение отзыва
    await update.message.reply_text("Спасибо за ваш отзыв! Нам важно ваше мнение.")

# Главная функция для запуска бота
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Оставить отзыв"), ask_feedback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()


