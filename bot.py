import os
from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from flask import Flask
from threading import Thread

# রেন্ডার সার্ভারকে সচল রাখার জন্য ছোট ফ্লাস্ক সার্ভার
app_web = Flask(__name__)

@app_web.route('/')
def home():
    print("Bot is alive!")
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)

# === আপনার ক্রেডেন্সিয়ালসমূহ ===
API_ID = 36023688
API_HASH = "2376e5a9aceca696f6fd7cd96fc5939c"
BOT_TOKEN = "9082103684:AAGDnZ-i9gzs2VAO5aRSvA4-ZOJAG3ffQI0"  # আপনার বট টোকেন নিশ্চিত করবেন

TMDB_BEARER_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1ZmFjZGNhMDAzZDU5Y2NkYjNlMTNiNzNmYWM1MjQ0OSIsIm5iZiI6MTc4NjM1MzY2OS45Miwic3ViIjoiNmE3OTk4MDU5ZWRiNjcxZTFjM2IxMWZmIiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.jfDOm1m8A8ilSKaKv4px8IIwvqjgc-DHN0KlWnLZ6k8"

bot = Client(
    "Movie_Finder_Bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("👋 স্বাগতম! যেকোনো মুভি বা ওয়েব সিরিজের নাম পাঠান। আমি তথ্য ও ডাউনলোড লিংক খুঁজে দেব।")

@bot.on_message(filters.text & ~filters.command(["start"]))
async def search_movie(client: Client, message: Message):
    query = message.text.strip()
    status_msg = await message.reply_text(f"🔍 **'{query}'** খোঁজা হচ্ছে, দয়া করে অপেক্ষা করুন...")

    try:
        url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=false&language=en-US&page=1"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_BEARER_TOKEN}"
        }

        response = requests.get(url, headers=headers, timeout=10)
        res = response.json()

        results = res.get("results", [])
        if not results:
            await status_msg.edit_text("❌ দুঃখিত, এই নামে কোনো মুভি পাওয়া যায়নি। সঠিক বানান দিয়ে আবার চেষ্টা করুন।")
            return

        movie = results[0]
        title = movie.get("title")
        release_date = movie.get("release_date", "তারিখ নেই")
        vote = movie.get("vote_average", "N/A")
        poster_path = movie.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        encoded_query = query.replace(" ", "+")
        google_link = f"https://www.google.com/search?q={encoded_query}+hindi+dubbed+download"
        telegram_search = f"https://t.me/s/search?q={encoded_query}"

        caption_text = (
            f"🎬 **মুভি:** {title}\n"
            f"📅 **রিলিজ:** {release_date} | ⭐ **রেটিং:** {vote}/10\n\n"
            f"🔗 **ডাউনলোড লিংকসমূহ:**\n"
            f"👉 [গুগل থেকে হিন্দি ডাবড ফাইল খুঁজুন]({google_link})\n"
            f"👉 [টেলিগ্রাম চ্যানেল থেকে খুঁজুন]({telegram_search})\n\n"
            f"🤖 *Powered by TMDB & Bot*"
        )

        if poster_url:
            await message.reply_photo(photo=poster_url, caption=caption_text)
            await status_msg.delete()
        else:
            await status_msg.edit_text(caption_text)

    except Exception as e:
        await status_msg.edit_text(f"⚠️ একটি ত্রুটি ঘটেছে: {str(e)}")

if __name__ == "__main__":
    # requirements.txt ফাইলে flask যোগ করতে ভুলবেন না
    t = Thread(target=run_web)
    t.start()
    print("Bot & Web server started successfully...")
    bot.run()
