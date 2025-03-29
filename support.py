import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

# Укажите ваш токен бота и Telegram ID администратора
TOKEN = "7525904539:AAHzE_r-B8Eqs2TYjVZP0_GfpLsscV0pwKk"
ADMIN_ID = 5084880209  # Замените на ваш Telegram ID

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Словарь для хранения отзывов пользователей
user_feedback = {}

# Функция для генерации Inline клавиатуры с рейтингом
def get_rating_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐️", callback_data="1"),
         InlineKeyboardButton("⭐⭐️", callback_data="2"),
         InlineKeyboardButton("⭐⭐⭐️", callback_data="3"),
         InlineKeyboardButton("⭐⭐⭐⭐️", callback_data="4"),
         InlineKeyboardButton("⭐⭐⭐⭐⭐️", callback_data="5")]
    ])

# Команда /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Добро пожаловать в наш ресторан! Пожалуйста, оставьте свой отзыв.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Оставить отзыв", callback_data="leave_feedback")]
        ])
    )

# Обработка кнопки "Оставить отзыв"
async def ask_rating(update: Update, context: CallbackContext):
    await update.callback_query.answer()  # Подтверждаем, что кнопка нажата
    await update.callback_query.edit_message_text("Пожалуйста, выберите ваш рейтинг от 1 до 5 звезд:",
                                                 reply_markup=get_rating_keyboard())

# Обработка выбранного рейтинга
async def handle_rating_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    rating = query.data  # Получаем выбранный рейтинг

    # Сохраняем рейтинг пользователя в словарь
    user_feedback[user_id] = {"rating": rating}

    # Просим пользователя оставить текстовый отзыв
    await query.answer()
    await query.edit_message_text("Спасибо за выбор рейтинга! Теперь, пожалуйста, напишите ваш отзыв:")

# Обработка текстовых сообщений (отзывы)
async def handle_feedback(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    feedback_text = update.message.text

    # Проверяем, есть ли у пользователя выбранный рейтинг
    if user_id not in user_feedback or "rating" not in user_feedback[user_id]:
        await update.message.reply_text("Пожалуйста, сначала выберите рейтинг!")
        return

    rating = user_feedback[user_id]["rating"]

    # Формируем полный отзыв с рейтингом
    feedback_message = f"Новый отзыв от @{update.message.from_user.username or update.message.from_user.full_name} ({update.message.from_user.id}):\n" \
                       f"Рейтинг: {rating} звезд\nОтзыв: {feedback_text}"

    # Отправляем отзыв администратору
    await context.bot.send_message(chat_id=ADMIN_ID, text=feedback_message)

    # Подтверждаем получение отзыва
    await update.message.reply_text("Спасибо за ваш отзыв! Нам важно ваше мнение.")

# Главная функция для настройки бота
def setup_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(ask_rating, pattern="leave_feedback"))
    app.add_handler(CallbackQueryHandler(handle_rating_selection, pattern="^[1-5]$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback))

    return app
