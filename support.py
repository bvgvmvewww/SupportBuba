from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import os

TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_CHAT_ID = "5084880209"

# Хранение отзывов
user_reviews = {}

# Flask app для Webhook
app = Flask(__name__)

# Основной код бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("⭐ Оставить отзыв")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Вы можете оставить отзыв, нажав на кнопку ниже.", reply_markup=reply_markup)

async def handle_review_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_reviews[user_id] = {
        "rating": None, "text": "", "username": update.message.from_user.username,
        "full_name": update.message.from_user.full_name
    }
    keyboard = [[KeyboardButton(f"⭐ {i}") for i in range(1, 6)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Выберите количество звезд:", reply_markup=reply_markup)

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    rating_text = update.message.text
    if user_id in user_reviews and "⭐" in rating_text:
        user_reviews[user_id]["rating"] = int(rating_text.replace("⭐", "").strip())
        await update.message.reply_text("Спасибо! Теперь напишите ваш отзыв или отправьте фото/видео/документ.", reply_markup=ReplyKeyboardRemove())

async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_reviews or user_reviews[user_id]["rating"] is None:
        await update.message.reply_text("Сначала выберите количество звезд!")
        return

    # Разделяем медиа и текст
    review_text = update.message.caption if update.message.caption else update.message.text

    if review_text:  # Если есть текст (подпись к фото или обычное сообщение)
        user_reviews[user_id]["text"] = review_text
        review_message = (
            f"🆔 ID: {user_id}\n"
            f"👤 @{user_reviews[user_id]['username'] if user_reviews[user_id]['username'] else 'Без никнейма'}\n"
            f"📛 {user_reviews[user_id]['full_name'] if user_reviews[user_id]['full_name'] else 'Имя не указано'}\n"
            f"⭐ Оценка: {user_reviews[user_id]['rating']}\n"
            f"📝 Отзыв: {review_text}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=review_message)

    # Обрабатываем медиа без подписи
    if update.message.photo:
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=update.message.photo[-1].file_id)
    if update.message.document:
        await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=update.message.document.file_id)
    if update.message.video:
        await context.bot.send_video(chat_id=ADMIN_CHAT_ID, video=update.message.video.file_id)

    del user_reviews[user_id]  # Чистим данные
    await update.message.reply_text("Спасибо за ваш отзыв! 😊")
    keyboard = [[KeyboardButton("⭐ Оставить отзыв")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Если захотите оставить еще один отзыв, нажмите кнопку ниже.", reply_markup=reply_markup)

# Flask роут для Webhook
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, app.bot)
    app.update_queue.put(update)
    return 'ok'

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("⭐ Оставить отзыв"), handle_review_request))
    application.add_handler(MessageHandler(filters.Regex("^⭐ [1-5]$"), handle_rating))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review))
    application.add_handler(MessageHandler(filters.PHOTO, handle_review))
    application.add_handler(MessageHandler(filters.Document(), handle_review))
    application.add_handler(MessageHandler(filters.VIDEO, handle_review))

    # Устанавливаем webhook
    application.bot.set_webhook(f'https://supportbuba.onrender.com')

    print("Бот запущен с Webhook...")
    
    # Запуск Flask сервера
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()

