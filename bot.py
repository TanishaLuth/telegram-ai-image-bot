import os
import aiohttp
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

# -----------------------------
# Environment variables
# -----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

# -----------------------------
# Initialize bot and dispatcher
# -----------------------------
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# -----------------------------
# Generate image from HuggingFace
# -----------------------------
async def generate_image(prompt: str):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(HF_MODEL_URL, headers=headers, json=payload) as resp:
                text = await resp.text()
                print(f"HuggingFace API status: {resp.status}, response: {text}")

                if resp.status != 200:
                    return None

                data = await resp.read()
                return data

        except Exception as e:
            print(f"Error during HuggingFace API request: {e}")
            return None

# -----------------------------
# Handlers
# -----------------------------
async def start_handler(message: types.Message):
    await message.reply(
        "🤖 Welcome to the AI Image Generator Bot!\n"
        "Send me any prompt, and I will generate an image for you.\n\n"
        "Example prompts:\n"
        "👉 'Solar system educational diagram'\n"
        "👉 'Printer showing paper path illustration'"
    )

async def prompt_handler(message: types.Message):
    prompt = message.text
    await message.reply("🎨 Generating your image… please wait (10–20 seconds).")
    img_bytes = await generate_image(prompt)

    if img_bytes is None:
        await message.reply("⚠️ Failed to generate image. Check logs or try again later.")
        return

    image_stream = BytesIO(img_bytes)
    image_stream.name = "image.png"
    image_stream.seek(0)
    await message.reply_photo(photo=image_stream)

# -----------------------------
# Register handlers using Aiogram 3.x filters
# -----------------------------
dp.message.register(start_handler, Command(commands=["start"]))
dp.message.register(prompt_handler)  # default handler for all text messages

# -----------------------------
# Run bot
# -----------------------------
if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(dp.start_polling(bot))
