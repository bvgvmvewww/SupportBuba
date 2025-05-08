import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ ЗАМЕНИ ТОКЕН ПЕРЕД ИСПОЛЬЗОВАНИЕМ
TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_CHAT_ID = 5084880209  # число, не строка

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище отзывов
user_reviews = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("⭐ Оставить отзыв")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Привет, это Буба!\n"
        "Очень рад, что вы заглянули к нам за драниками.\n"
        "Если есть минутка — расскажите, как всё прошло?\n"
        "Каждый ваш отзыв помогает сделать наши драники ещё вкуснее.",
        reply_markup=reply_markup
    )

# Начало отзыва — запрос оценки
async def handle_review_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_reviews[user_id] = {
        "rating": None,
        "text": "",
        "username": update.message.from_user.username or "Без никнейма",
        "full_name": update.message.from_user.full_name or "Имя не указано"
    }
    keyboard = [[KeyboardButton(f"⭐ {i}") for i in range(1, 6)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Выберите количество звёзд:", reply_markup=reply_markup)

# Обработка оценки
async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    rating_text = update.message.text

    if user_id in user_reviews and "⭐" in rating_text:
        try:
            user_reviews[user_id]["rating"] = int(rating_text.replace("⭐", "").strip())
        except ValueError:
            await update.message.reply_text("Некорректный формат оценки.")
            return

        await update.message.reply_text(
            "Спасибо за оценку!\n"
            "А теперь — пару слов?\n"
            "Расскажите, что понравилось (или что стоит подкрутить).\n"
            "Можно просто текст, а можно фото — я всё внимательно прочитаю!",
            reply_markup=ReplyKeyboardRemove()
        )

# Обработка текста и медиа-отзывов
async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_reviews or user_reviews[user_id]["rating"] is None:
        await update.message.reply_text("Пожалуйста, сначала выберите количество звёзд.")
        return

    # Получаем текст (из caption или текстового сообщения)
    review_text = update.message.caption or update.message.text
    if review_text:
        user_reviews[user_id]["text"] = review_text

    username = user_reviews[user_id]["username"]
    full_name = user_reviews[user_id]["full_name"]
    rating = user_reviews[user_id]["rating"]

    review_message = (
        f"🆔 ID: {user_id}\n"
        f"👤 @{username}\n"
        f"📛 {full_name}\n"
        f"⭐ Оценка: {rating}\n"
        f"📝 Отзыв: {user_reviews[user_id]['text'] or '—'}"
    )

    # Отправка текста админу
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=review_message)

    # Отправка медиа
    if update.message.photo:
        await context.bot.send_photo(chat_id=ADMIN_CHAT_ID, photo=update.message.photo[-1].file_id)
    if update.message.document:
        await context.bot.send_document(chat_id=ADMIN_CHAT_ID, document=update.message.document.file_id)
    if update.message.video:
        await context.bot.send_video(chat_id=ADMIN_CHAT_ID, video=update.message.video.file_id)

    # Очистка
    del user_reviews[user_id]

    # Благодарим пользователя
    await update.message.reply_text(
        "Спасибо за отзыв!\n"
        "Буба всё прочитал 👍\n"
        "Каждый ваш отзыв помогает нам становиться вкуснее и лучше. Ждём в гости снова! 💫"
    )

    keyboard = [[KeyboardButton("⭐ Оставить отзыв")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Если захотите оставить ещё один отзыв, нажмите кнопку ниже.",
        reply_markup=reply_markup
    )

# Основной запуск
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("⭐ Оставить отзыв"), handle_review_request))
    app.add_handler(MessageHandler(filters.Regex("^⭐ [1-5]$"), handle_rating))

    # Обработка медиа + текста
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_review))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
