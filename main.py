import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask, send_from_directory
from threading import Thread

TOKEN = os.environ.get("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

UPLOAD_FOLDER = "downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

@app.route(f"/{UPLOAD_FOLDER}/<path:filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        file = None
        file_name = None

        if message.document:
            file = await message.document.get_file()
            file_name = message.document.file_name
        elif message.photo:
            file = await message.photo[-1].get_file()
            file_name = f"{message.photo[-1].file_id}.jpg"
        elif message.video:
            file = await message.video.get_file()
            file_name = f"{message.video.file_id}.mp4"
        else:
            await message.reply_text("فقط عکس، ویدیو یا فایل بفرست.")
            return

        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        await file.download_to_drive(file_path)

        repl_url = os.environ.get("RENDER_EXTERNAL_URL")
        download_url = f"{repl_url}{UPLOAD_FOLDER}/{file_name}"
        await message.reply_text(f"✅ لینک دانلود:\n{download_url}")

    except Exception as e:
        await update.message.reply_text("❌ خطا در پردازش فایل.")
        print(f"Error: {e}")

if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_file))
    app.run_polling()
