from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import sqlite3

TOKEN = "7784805270:AAFgPjPeKbliS7vqKTw9oGZbNo-XVxLmPP0"
ADMIN_ID = 5402911845  # Замените на ваш ID


# Инициализация БД
def init_db():
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()


# Сохранение пользователя
def save_user(user_id):
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text("✅ Вы подписаны на рассылку!")


# Обработка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Доступ запрещен!")
        return

    photo = update.message.photo[-1]  # Самое качественное изображение
    caption = update.message.caption or ""

    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    subscribers = c.fetchall()
    conn.close()

    for (user_id,) in subscribers:
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo.file_id,
                caption=caption
            )
        except Exception as e:
            print(f"Ошибка отправки для {user_id}: {e}")

    await update.message.reply_text(f"📨 Отправлено {len(subscribers)} пользователям!")


def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_photo))

    app.run_polling()


if __name__ == '__main__':
    main()