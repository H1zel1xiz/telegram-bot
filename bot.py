from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

BOT_TOKEN = '7905345541:AAFBRykd84gokahizMRp3BhocYLd9FDREgM'
ADMIN_IDS = [1267048446, 7057690959]  # два администратора
WAITING_FOR_APPLICATION = 1

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['state'] = None
    keyboard = [
        [InlineKeyboardButton("Подать заявку", callback_data="apply")],
        [InlineKeyboardButton("Связаться с админом", callback_data="contact")],
        [InlineKeyboardButton("Донат", callback_data="donate")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Выберите действие:", reply_markup=reply_markup)

# Обработка кнопок меню
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "apply":
        questions = (
            "Пожалуйста, ответьте одним сообщением на следующие вопросы:\n\n"
            "1. Как тебя зовут и сколько тебе лет?\n"
            "(Минимальный возраст, например: 13+)\n\n"
            "2. Откуда ты узнал о нашем сервере?\n"
            "(YouTube, друзья, TikTok, Discord и т.д.)\n\n"
            "3. Почему ты хочешь играть именно у нас?\n\n"
            "4. Чем ты хочешь заниматься на сервере?\n"
            "(Фермы, строительство, РП, PvP и т.д.)\n\n"
            "5. Твой ник в Minecraft (Java Edition)\n\n"
            "6. Был ли у тебя опыт игры на приватных серверах?\n"
            "(Да/Нет. Если да — на каких?)\n\n"
            "7. Нарушал ли ты когда-либо правила на серверах?\n"
            "(Будь честным — это не дисквалификация)\n\n"
            "8. Есть ли у тебя микрофон / ты пользуешься голосовым чатом?\n\n"
            "9. Умеешь ли ты строить красиво? Есть ли скрины/мир?"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="back_to_menu")]
        ])
        context.user_data['state'] = WAITING_FOR_APPLICATION
        await query.message.edit_text(questions, reply_markup=keyboard)

    elif query.data == "contact":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="back_to_menu")]
        ])
        context.user_data['state'] = None
        await query.message.edit_text(
            "Чтобы связаться с админом, напишите: @h1zel1xiz",
            reply_markup=keyboard
        )

    elif query.data == "donate":
        donate_text = (
            "───────────────────────\n"
            "🎨 Цветной ник в игре.\n\n"
            "Вы можете поставить себе цветной ник любого цвета!\n\n"
            "💵 Цена: 30 грн (50 рублей)\n"
            "───────────────────────\n"
            "🏷 Префикс в игре.\n\n"
            "Вы получите префикс в игре, который будут видеть все игроки сервера.\n"
            "❗ Запрещено кого-то оскорблять в префиксе\n\n"
            "💵 Цена: 80 грн (150 рублей)\n"
            "───────────────────────\n"
            "🔓 Разбан.\n\n"
            "Вы будете разбанены, не важно от того что вы сделали\n\n"
            "💵 Цена: 200 грн (373 рублей)\n"
            "───────────────────────\n\n"
            "Для оформления доната пишите в телеграм: @h1zel1xiz\n\n"
            "❗❗❗ ВАЖНО: комиссию оплачивает покупатель доната."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Назад", callback_data="back_to_menu")]
        ])
        context.user_data['state'] = None
        await query.message.edit_text(donate_text, reply_markup=keyboard)

    elif query.data == "back_to_menu":
        context.user_data['state'] = None
        await start(update, context)

# Обработка ответа пользователя
async def handle_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') != WAITING_FOR_APPLICATION:
        return

    application_text = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Без ника"

    context.user_data['state'] = None

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✓ Принять", callback_data=f"accept_{user_id}")],
        [InlineKeyboardButton("✗ Отклонить", callback_data=f"reject_{user_id}")]
    ])

    msg = (
        f"Новая заявка от @{username} (ID: {user_id}):\n\n"
        f"{application_text}"
    )

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin_id, text=msg, reply_markup=keyboard)

    await update.message.reply_text("Спасибо! Ваша заявка отправлена.")
    context.application.chat_data[user_id] = {
        'username': username
    }

# Обработка кнопок админа
async def admin_decision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("accept_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id,
            text="Поздравляем! Вы приняты. Вот ссылка на группу: https://t.me/+FvIzcsmlSbk2YmUy"
        )
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"✅ Заявка от {user_id} одобрена."
        )

    elif data.startswith("reject_"):
        user_id = int(data.split("_")[1])
        await context.bot.send_message(
            chat_id=user_id,
            text="К сожалению, ваша заявка была отклонена."
        )
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=f"❌ Заявка от {user_id} отклонена."
        )

# Команда /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['state'] = None
    await update.message.reply_text("Операция отменена.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(apply|contact|donate|back_to_menu)$"))
    app.add_handler(CallbackQueryHandler(admin_decision_handler, pattern="^(accept|reject)_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_application))
    app.add_handler(CommandHandler("cancel", cancel))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
