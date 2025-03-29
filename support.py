from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_CHAT_ID = "5084880209"

# Хранение отзывов
user_reviews = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("⭐ Оставить отзыв")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("Привет! Вы можете оставить отзыв, нажав на кнопку ниже.", reply_markup=reply_markup)

async def handle_review_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_reviews[user_id] = {"rating": None, "text": "", "username": update.message.from_user.username, "full_name": update.message.from_user.full_name}
    
    keyboard = [
        [KeyboardButton("⭐ 1"), KeyboardButton("⭐ 2"), KeyboardButton("⭐ 3")],
        [KeyboardButton("⭐ 4"), KeyboardButton("⭐ 5")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text("Пожалуйста, выберите количество звезд:", reply_markup=reply_markup)

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    rating_text = update.message.text

    if user_id in user_reviews and "⭐" in rating_text:
        user_reviews[user_id]["rating"] = int(rating_text.replace("⭐", "").strip())

        # Убираем клавиатуру с выбором звезд
        await update.message.reply_text("Спасибо! Теперь напишите ваш отзыв текстом.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("Пожалуйста, выберите количество звезд!")

async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    review_text = update.message.text

    if user_id in user_reviews and user_reviews[user_id]["rating"] is not None:
        user_reviews[user_id]["text"] = review_text
        rating = user_reviews[user_id]["rating"]
        username = user_reviews[user_id]["username"]
        full_name = user_reviews[user_id]["full_name"]

        # Формируем данные пользователя
        user_info = f"🆔 ID: {user_id}\n"
        if username:
            user_info += f"👤 Никнейм: @{username}\n"
        user_info += f"📛 Имя: {full_name}\n"

        # Отправляем админу
        review_message = f"{user_info}⭐ Оценка: {rating}\n📝 Отзыв: {review_text}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=review_message)

        await update.message.reply_text("Спасибо за ваш отзыв! 😊")
        del user_reviews[user_id]  # Удаляем из памяти
    else:
        await update.message.reply_text("Сначала выберите количество звезд!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("⭐ Оставить отзыв"), handle_review_request))
    app.add_handler(MessageHandler(filters.Regex("^⭐ [1-5]$"), handle_rating))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()