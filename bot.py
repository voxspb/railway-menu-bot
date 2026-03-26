import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

MENU_BOT_TOKEN = os.getenv("MENU_BOT_TOKEN", "")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID", "")  # group chat id with OpenClaw bot

if not MENU_BOT_TOKEN:
    raise RuntimeError("MENU_BOT_TOKEN is missing")
if not TARGET_CHAT_ID:
    raise RuntimeError("TARGET_CHAT_ID is missing")

STATE = {}

MAIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("💸 Финансы"), KeyboardButton("👶 Ася")],
    [KeyboardButton("🔔 Оповещения"), KeyboardButton("📅 Календарь")],
], resize_keyboard=True)

FIN_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("💸 Расход"), KeyboardButton("💰 Доход")],
    [KeyboardButton("📊 Статистика"), KeyboardButton("⬅️ Назад")],
], resize_keyboard=True)

ASYA_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("📏 Замер"), KeyboardButton("📈 График роста")],
    [KeyboardButton("🧪 Анализы"), KeyboardButton("👩‍⚕️ Врач")],
    [KeyboardButton("⬅️ Назад")],
], resize_keyboard=True)

ALERT_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("➕ Добавить"), KeyboardButton("📋 Список")],
    [KeyboardButton("⬅️ Назад")],
], resize_keyboard=True)

CAL_MENU = ReplyKeyboardMarkup([
    [KeyboardButton("➕ Событие"), KeyboardButton("📋 Сегодня")],
    [KeyboardButton("⬅️ Назад")],
], resize_keyboard=True)


def set_state(chat_id, state):
    STATE[chat_id] = state


def clear_state(chat_id):
    STATE.pop(chat_id, None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню", reply_markup=MAIN_MENU)


async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"chat_id: {update.effective_chat.id}")


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # Main menu
    if text == "💸 Финансы":
        clear_state(chat_id)
        await update.message.reply_text("Финансы", reply_markup=FIN_MENU)
        return

    if text == "👶 Ася":
        clear_state(chat_id)
        await update.message.reply_text("Ася", reply_markup=ASYA_MENU)
        return

    if text == "🔔 Оповещения":
        clear_state(chat_id)
        await update.message.reply_text("Оповещения", reply_markup=ALERT_MENU)
        return

    if text == "📅 Календарь":
        clear_state(chat_id)
        await update.message.reply_text("Календарь", reply_markup=CAL_MENU)
        return

    if text == "⬅️ Назад":
        clear_state(chat_id)
        await update.message.reply_text("Главное меню", reply_markup=MAIN_MENU)
        return

    # Submenus
    if text == "💸 Расход":
        set_state(chat_id, "await_spend")
        await update.message.reply_text("Введи: сумма категория [коммент]\nНапример: 500 продукты хлеб")
        return

    if text == "💰 Доход":
        set_state(chat_id, "await_income")
        await update.message.reply_text("Введи: сумма источник [коммент]\nНапример: 50000 зарплата")
        return

    if text == "📊 Статистика":
        await forward_to_openclaw("Покажи финансы: сегодня/неделя/месяц и категории")
        await update.message.reply_text("Запросил статистику у ассистента.")
        return

    if text == "📏 Замер":
        set_state(chat_id, "await_measure")
        await update.message.reply_text("Введи: рост вес [заметки]\nНапример: 92 13.6 хороший аппетит")
        return

    if text == "📈 График роста":
        await forward_to_openclaw("Покажи график роста и последние замеры")
        await update.message.reply_text("Запросил график роста у ассистента.")
        return

    if text == "🧪 Анализы":
        set_state(chat_id, "await_scan")
        await update.message.reply_text("Пришли фото анализов и короткое описание.")
        return

    if text == "👩‍⚕️ Врач":
        set_state(chat_id, "await_doctor")
        await update.message.reply_text("Введи: дата время врач место\nНапример: 12.04 15:30 педиатр клиника X")
        return

    if text == "➕ Добавить":
        set_state(chat_id, "await_alert")
        await update.message.reply_text("Введи напоминание: дата/время + текст\nНапример: 26.04 12:00 Сделать замеры")
        return

    if text == "📋 Список":
        await forward_to_openclaw("Покажи список активных напоминаний")
        await update.message.reply_text("Запросил список напоминаний.")
        return

    if text == "➕ Событие":
        set_state(chat_id, "await_event")
        await update.message.reply_text("Введи событие: дата/время + текст\nНапример: 01.05 19:00 Ужин у родителей")
        return

    if text == "📋 Сегодня":
        await forward_to_openclaw("План/календарь на сегодня")
        await update.message.reply_text("Запросил план на сегодня.")
        return

    # Handle stateful input
    state = STATE.get(chat_id)
    if state == "await_spend":
        await forward_to_openclaw(f"Добавь расход: {text}")
        clear_state(chat_id)
        await update.message.reply_text("Расход отправлен ассистенту.", reply_markup=FIN_MENU)
        return

    if state == "await_income":
        await forward_to_openclaw(f"Добавь доход: {text}")
        clear_state(chat_id)
        await update.message.reply_text("Доход отправлен ассистенту.", reply_markup=FIN_MENU)
        return

    if state == "await_measure":
        await forward_to_openclaw(f"Запиши замер ребёнка: {text}")
        clear_state(chat_id)
        await update.message.reply_text("Замер отправлен ассистенту.", reply_markup=ASYA_MENU)
        return

    if state == "await_doctor":
        await forward_to_openclaw(f"Запись к врачу: {text}")
        clear_state(chat_id)
        await update.message.reply_text("Запрос отправлен ассистенту.", reply_markup=ASYA_MENU)
        return

    if state == "await_alert":
        await forward_to_openclaw(f"Создай напоминание: {text}")
        clear_state(chat_id)
        await update.message.reply_text("Напоминание отправлено ассистенту.", reply_markup=ALERT_MENU)
        return

    if state == "await_event":
        await forward_to_openclaw(f"Добавь событие в календарь: {text}")
        clear_state(chat_id)
        await update.message.reply_text("Событие отправлено ассистенту.", reply_markup=CAL_MENU)
        return

    # Default: pass-through
    await forward_to_openclaw(text)
    await update.message.reply_text("Передал сообщение ассистенту.")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    state = STATE.get(chat_id)
    if state == "await_scan":
        # Forward photo to OpenClaw chat
        await context.bot.send_message(chat_id=TARGET_CHAT_ID, text="Прикладываю анализы (фото ниже) + описание от пользователя.")
        await update.message.forward(chat_id=TARGET_CHAT_ID)
        clear_state(chat_id)
        await update.message.reply_text("Фото отправлено ассистенту.", reply_markup=ASYA_MENU)
        return

    await update.message.reply_text("Фото получено, но не понял контекст. Нажми кнопку из меню.")


async def forward_to_openclaw(text: str):
    # send text into the shared group chat where OpenClaw bot is present
    from telegram import Bot
    bot = Bot(token=MENU_BOT_TOKEN)
    await bot.send_message(chat_id=TARGET_CHAT_ID, text=text)


def main():
    app = ApplicationBuilder().token(MENU_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
