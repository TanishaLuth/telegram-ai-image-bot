import os
import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web

# -----------------------------
# Environment variables
# -----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
LANGUAGETOOL_API_URL = "https://api.languagetool.org/v2/check"

# -----------------------------
# Initialize bot and dispatcher
# -----------------------------
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# -----------------------------
# Check spelling using LanguageTool
# -----------------------------
async def check_spelling(word: str):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"text={word}&language=en-US"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(LANGUAGETOOL_API_URL, headers=headers, data=data) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(f"LanguageTool API Error: {resp.status}, {text}")
                    return None

                result = await resp.json()
                return result

        except Exception as e:
            print(f"Error during LanguageTool API request: {e}")
            return None

# -----------------------------
# Telegram Handlers
# -----------------------------
async def start_handler(message: types.Message):
    await message.reply(
        "🤖 Welcome to the Spelling Checker Bot!\n"
        "Send me a **single word**, and I will check for spelling mistakes.\n\n"
        "Example:\n"
        "👉 'congrtulion'\n"
        "👉 'appel'"
    )

async def spell_handler(message: types.Message):
    word = message.text.strip()

    # Check if only one word
    if len(word.split()) != 1:
        await message.reply("⚠️ Please send **only one word** at a time.")
        return

    await message.reply("🔍 Checking spelling…")

    result = await check_spelling(word)
    if result is None:
        await message.reply("⚠️ Failed to check spelling. Try again later.")
        return

    matches = result.get("matches", [])
    if not matches:
        await message.reply(f"✅ No spelling mistakes found for '{word}'.")
        return

    # Only consider the first match for simplicity
    match = matches[0]
    short_message = match.get("shortMessage", "Possible mistake")
    replacements = match.get("replacements", [])

    if replacements:
        correction = replacements[0].get("value", "No suggestion")
    else:
        correction = "No suggestion"

    reply_text = f"⚠️ {short_message} detected.\nSuggested correction: {correction}"
    await message.reply(reply_text)

# -----------------------------
# Register handlers (Aiogram 3.x)
# -----------------------------
dp.message.register(start_handler, Command("start"))
dp.message.register(spell_handler)

# -----------------------------
# Aiohttp Web Server (FOR RENDER)
# -----------------------------
async def web_handler(request):
    return web.Response(text="Bot is running on Render — OK")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", web_handler)

    port = int(os.environ.get("PORT", 10000))  # Render provides PORT
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server running on port {port}")

# -----------------------------
# Main Application Runner
# -----------------------------
async def main():
    # Start Render webserver
    await start_webserver()

    # Start Telegram bot polling
    await dp.start_polling(bot)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    print("Starting bot on Render...")
    asyncio.run(main())
