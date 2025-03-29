from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_CHAT_ID = "5084880209"

# Хранение отзывов (user_id: {rating: int, text: str})
user_reviews = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("⭐ Оставить отзыв", callback_data="leave_review")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажмите на кнопку, чтобы оставить отзыв.", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "leave_review":
        keyboard = [
            [InlineKeyboardButton("⭐", callback_data="rate_1"),
             InlineKeyboardButton("2⭐", callback_data="rate_2"),
             InlineKeyboardButton("3⭐", callback_data="rate_3"),
             InlineKeyboardButton("4⭐", callback_data="rate_4"),
             InlineKeyboardButton("5⭐", callback_data="rate_5")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Пожалуйста, выберите количество звезд:", reply_markup=reply_markup)

    elif query.data.startswith("rate_"):
        user_id = query.from_user.id
        user_reviews[user_id] = {
            "rating": int(query.data.split("_")[1]),
            "text": "",
            "username": query.from_user.username,
            "full_name": query.from_user.full_name
        }
        await query.message.reply_text("Спасибо! Теперь напишите ваш отзыв текстом.")

async def handle_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    review_text = update.message.text

    if user_id in user_reviews:
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
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_review))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
