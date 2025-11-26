import os
import aiohttp
from io import BytesIO
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiohttp import web

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
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}

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
# Telegram Handlers
# -----------------------------
async def start_handler(message: types.Message):
    await message.reply(
        "🤖 Welcome to the AI Image Generator Bot!\n"
        "Send me a prompt and I will generate an image.\n\n"
        "Example prompts:\n"
        "👉 'Solar system educational diagram'\n"
        "👉 'Printer showing paper path illustration'"
    )

async def prompt_handler(message: types.Message):
    prompt = message.text
    await message.reply("🎨 Generating your image… please wait (10–20 seconds).")
    img_bytes = await generate_image(prompt)

    if img_bytes is None:
        await message.reply("⚠️ Failed to generate image. Try again later.")
        return

    image_stream = BytesIO(img_bytes)
    image_stream.name = "image.png"
    image_stream.seek(0)
    await message.reply_photo(photo=image_stream)

# Register handlers (Aiogram 3.x)
dp.message.register(start_handler, Command("start"))
dp.message.register(prompt_handler)

# -----------------------------
# Aiohttp Web Server (FOR RENDER)
# -----------------------------
async def web_handler(request):
    return web.Response(text="Bot is running on Render — OK")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", web_handler)

    port = int(os.environ.get("PORT", 10000))  # Render gives PORT
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server running on port {port}")

# -----------------------------
# Main Application Runner
# -----------------------------
async def main():
    # Start tiny web server so Render detects the port
    await start_webserver()

    # Start Telegram bot polling
    await dp.start_polling(bot)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    print("Starting bot on Render...")
    asyncio.run(main())
