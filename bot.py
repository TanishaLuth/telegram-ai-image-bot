import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")

# HuggingFace model endpoint (SDXL)
HF_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Welcome to the AI Image Generator Bot!\n"
        "Just send me any prompt, and I will generate an image for you.\n\n"
        "Example:\n"
        "👉 'Solar system educational diagram'\n"
        "👉 'A printer showing paper path illustration'\n"
    )


def generate_image(prompt):
    payload = {"inputs": prompt}
    response = requests.post(HF_MODEL_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        return None

    return response.content


async def handle_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = update.message.text

    await update.message.reply_text("🎨 Generating your image… please wait (10–20 seconds).")

    img_bytes = generate_image(user_prompt)

    if img_bytes is None:
        await update.message.reply_text("⚠️ Failed to generate image. Try again later.")
        return

    await update.message.reply_photo(photo=img_bytes)


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_prompt))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
