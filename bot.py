import os
import aiohttp
import asyncio
from io import BytesIO
from aiogram import Bot, Dispatcher, types

# Environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HF_API_KEY")
HF_MODEL_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

# Initialize bot
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)
dp.start_polling(bot)

async def generate_image(prompt: str):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}  # Wait for model to load if necessary
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(HF_MODEL_URL, headers=headers, json=payload) as resp:
                text = await resp.text()
                print(f"HuggingFace API status: {resp.status}, response: {text}")  # For Render logs

                if resp.status != 200:
                    return None

                data = await resp.read()
                return data

        except Exception as e:
            print(f"Error during HuggingFace API request: {e}")
            return None

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply(
        "🤖 Welcome to the AI Image Generator Bot!\n"
        "Send me any prompt, and I will generate an image for you.\n\n"
        "Example:\n"
        "👉 'Solar system educational diagram'\n"
        "👉 'Printer showing paper path illustration'"
    )

@dp.message_handler()
async def handle_prompt(message: types.Message):
    prompt = message.text
    await message.reply("🎨 Generating your image… please wait (10–20 seconds).")
    img_bytes = await generate_image(prompt)

    if img_bytes is None:
        await message.reply("⚠️ Failed to generate image. Try again later.")
        return

    # Send image to Telegram
    image_stream = BytesIO(img_bytes)
    image_stream.name = "image.png"
    image_stream.seek(0)
    await message.reply_photo(photo=image_stream)

if __name__ == "__main__":
    print("Bot is running...")
    asyncio.run(dp.start_polling())


