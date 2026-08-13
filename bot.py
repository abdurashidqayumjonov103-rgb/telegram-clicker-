import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-domain.render.com")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    start_param = args[0] if args else ""
    
    app_url = f"{WEBAPP_URL}?start_param={start_param}" if start_param else WEBAPP_URL
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 PLAY NOW", web_app=WebAppInfo(url=app_url))]
    ])
    
    await update.message.reply_text(
        f"Xush kelibsiz, {user.first_name}! 👇 Quyidagi tugmani bosib clicker o'yinini boshlang:",
        reply_markup=keyboard
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot ishga tushdi...")
    app.run_polling()
