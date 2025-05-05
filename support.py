from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_CHAT_ID = "5084880209"

# Хранение отзывов
user_reviews = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("⭐ Оставить отзыв")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет, это Буба!\n"
    "Очень рад, что вы заглянули к нам за драниками.\n"
    "Если есть минутка — расскажите, как всё прошло?\n"
    "Каждый ваш отзыв помогает сделать наши драники ещё вкуснее.", reply_markup=reply_markup)

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
        await update.message.reply_text("Спасибо за оценку!\n"
        "А теперь — пару слов?\n"
        "Расскажите, что понравилось (или что стоит подкрутить).\n"
        "Можно просто текст, а можно фото — я всё внимательно прочитаю!.", reply_markup=ReplyKeyboardRemove())

async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_reviews or user_reviews[user_id]["rating"] is None:
        await update.message.reply_text("Пожалуйста, укажите количество звезд!")
        return

    # Разделяем медиа и текст
    review_text = update.message.caption if update.message.caption else update.message.text

    if review_text:  # Если есть текст (подпись к фото/видео или обычное сообщение)
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
    await update.message.reply_text("Спасибо за отзыв!\n"
    "Буба всё прочитал👍\n"
    "Каждый ваш отзыв помогает нам становиться вкуснее и лучше. Ждем в гости снова! 💫"
    keyboard = [[KeyboardButton("⭐ Оставить отзыв")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Если захотите оставить еще один отзыв, нажмите кнопку ниже.", reply_markup=reply_markup)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("⭐ Оставить отзыв"), handle_review_request))
    app.add_handler(MessageHandler(filters.Regex("^⭐ [1-5]$"), handle_rating))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review))
    app.add_handler(MessageHandler(filters.PHOTO, handle_review))
    app.add_handler(MessageHandler(filters.Document(), handle_review))
    app.add_handler(MessageHandler(filters.VIDEO, handle_review))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
