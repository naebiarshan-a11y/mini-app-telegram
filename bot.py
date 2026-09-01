import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")
if not WEB_APP_URL:
    raise RuntimeError("WEB_APP_URL environment variable is not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = InlineKeyboardButton(
        text="🚀 ورود به Mini App",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    await update.message.reply_text(
        "سلام 👋\nبرای باز کردن مینی‌اپ روی دکمه زیر بزن:",
        reply_markup=InlineKeyboardMarkup([[button]])
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
