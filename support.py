import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import os
from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)


# Укажите ваш токен бота и Telegram ID администратора
TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_ID = 5084880209  # Замените на ваш Telegram ID

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Клавиатура для выбора рейтинга (5 звезд)
rating_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("⭐️")],
        [KeyboardButton("⭐⭐️")],
        [KeyboardButton("⭐⭐⭐️")],
        [KeyboardButton("⭐⭐⭐⭐️")],
        [KeyboardButton("⭐⭐⭐⭐⭐️")]
    ],
    resize_keyboard=True
)

# Команда /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Добро пожаловать в наш ресторан! Пожалуйста, оставьте свой отзыв.", 
        reply_markup=rating_keyboard
    )

# Обработка выбора рейтинга
async def ask_feedback(update: Update, context: CallbackContext):
    user = update.message.from_user
    rating = update.message.text
    
    if rating in ["⭐️", "⭐⭐️", "⭐⭐⭐️", "⭐⭐⭐⭐️", "⭐⭐⭐⭐⭐️"]:
        context.user_data['rating'] = rating  # Сохраняем выбранный рейтинг
        await update.message.reply_text("Спасибо за ваш выбор! Пожалуйста, напишите ваш отзыв:")
    else:
        await update.message.reply_text("Пожалуйста, выберите рейтинг от 1 до 5 звезд.")

# Обработка текстовых сообщений (отзывы)
async def handle_feedback(update: Update, context: CallbackContext):
    user = update.message.from_user
    rating = context.user_data.get('rating', 'Не указан')
    feedback_text = f"Новый отзыв от @{user.username or user.full_name} ({user.id}):\n" \
                    f"Рейтинг: {rating}\n{update.message.text}"

    # Отправляем отзыв администратору
    await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_text)

    # Подтверждаем получение отзыва
    await update.message.reply_text("Спасибо за ваш отзыв! Нам важно ваше мнение.")

# Главная функция для запуска бота
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("⭐️|⭐⭐️|⭐⭐⭐️|⭐⭐⭐⭐️|⭐⭐⭐⭐⭐️"), ask_feedback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

