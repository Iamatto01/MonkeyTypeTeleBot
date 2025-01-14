import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import requests

# Load environment variables from a .env file
load_dotenv("envi.env")

# Temporary storage for API keys (use a real database in production)
user_api_keys = {}

# Utility function to fetch data from Monkeytype API
def fetch_from_api(endpoint: str, api_key: str, params=None):
    try:
        url = f"https://api.monkeytype.com{endpoint}"
        headers = {"Authorization": f"ApeKey {api_key}"}
        response = requests.get(url, headers=headers, params=params)
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    welcome_message = (
        "Welcome to the Monkeytype Tracker Bot! 🎉\n\n"
        "Set your Monkeytype API key first with /setapikey.\n\n"
        "Available commands:\n"
        "/recentresult - View your most recent typing test\n"
        "/checkpersonalbest - View your personal best stats\n"
        "/news - View the latest public service announcements\n"
        "/histogram - View a histogram of typing speed distribution\n"
    )
    await update.message.reply_text(welcome_message)

async def set_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the user's Monkeytype API key."""
    if not context.args:
        await update.message.reply_text("Please provide your Monkeytype API key. Usage: /setapikey <YOUR_API_KEY>")
        return

    api_key = context.args[0]
    user_id = update.effective_user.id
    user_api_keys[user_id] = api_key

    await update.message.reply_text("Your API key has been saved! ✅ Now you can use other commands.")

async def recent_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display the user's most recent result."""
    user_id = update.effective_user.id
    api_key = user_api_keys.get(user_id)

    if not api_key:
        await update.message.reply_text("You need to set your API key first with /setapikey.")
        return

    endpoint = "/results/last"
    status_code, response_data = fetch_from_api(endpoint, api_key)

    if status_code == 200:
        data = response_data.get("data", {})
        result_message = (
            "📋 *Your Most Recent Typing Test* 📋\n\n"
            f" - Mode: {data.get('mode')}\n"
            f" - WPM: {data.get('wpm')}\n"
            f" - Accuracy: {data.get('acc')}%\n"
            f" - Consistency: {data.get('consistency')}%\n"
            f" - Test Duration: {data.get('testDuration')} seconds\n"
        )
        await update.message.reply_text(result_message, parse_mode="Markdown")
    elif status_code == 401:
        await update.message.reply_text("Authentication error. Please check your API key.")
    else:
        await update.message.reply_text(f"Failed to fetch recent result. Status: {status_code}")

async def check_personal_best(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display the user's personal bests."""
    user_id = update.effective_user.id
    api_key = user_api_keys.get(user_id)

    if not api_key:
        await update.message.reply_text("You need to set your API key first with /setapikey.")
        return

    endpoint = "/results"
    params = {"limit": 1000}
    status_code, response_data = fetch_from_api(endpoint, api_key, params)

    if status_code == 200:
        results = response_data.get("data", [])
        categories = {
            "15 seconds": None,
            "30 seconds": None,
            "60 seconds": None,
            "120 seconds": None,
            "10 words": None,
            "25 words": None,
            "50 words": None,
            "100 words": None,
        }

        for result in results:
            mode = result.get("mode")
            duration = result.get("testDuration")
            word_count = int(result.get("mode2", 0)) if result.get("mode2", "0").isdigit() else None
            wpm = result.get("wpm")

            if mode == "time":
                if duration == 15 and (categories["15 seconds"] is None or wpm > categories["15 seconds"]):
                    categories["15 seconds"] = wpm
                elif duration == 30 and (categories["30 seconds"] is None or wpm > categories["30 seconds"]):
                    categories["30 seconds"] = wpm
                elif duration == 60 and (categories["60 seconds"] is None or wpm > categories["60 seconds"]):
                    categories["60 seconds"] = wpm
                elif duration == 120 and (categories["120 seconds"] is None or wpm > categories["120 seconds"]):
                    categories["120 seconds"] = wpm
            elif mode == "words" and word_count:
                if word_count == 10 and (categories["10 words"] is None or wpm > categories["10 words"]):
                    categories["10 words"] = wpm
                elif word_count == 25 and (categories["25 words"] is None or wpm > categories["25 words"]):
                    categories["25 words"] = wpm
                elif word_count == 50 and (categories["50 words"] is None or wpm > categories["50 words"]):
                    categories["50 words"] = wpm
                elif word_count == 100 and (categories["100 words"] is None or wpm > categories["100 words"]):
                    categories["100 words"] = wpm

        valid_wpm_values = [wpm for wpm in categories.values() if wpm is not None]
        average_wpm = sum(valid_wpm_values) / len(valid_wpm_values) if valid_wpm_values else None

        pb_message = "🏆 *Your Personal Bests* 🏆\n\n"
        for category, wpm in categories.items():
            pb_message += f" - {category}: {wpm if wpm else 'No data available'} WPM\n"
        
        if average_wpm is not None:
            pb_message += f"\n📊 *Average WPM*: {average_wpm:.2f}"
        else:
            pb_message += "\n📊 *Average WPM*: No data available"

        await update.message.reply_text(pb_message, parse_mode="Markdown")
    elif status_code == 401:
        await update.message.reply_text("Authentication error. Please check your API key.")
    else:
        await update.message.reply_text(f"Failed to fetch personal bests. Status: {status_code}")

async def fetch_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display the latest public service announcements."""
    endpoint = "/psa"
    status_code, response_data = fetch_from_api(endpoint, "")

    if status_code == 200:
        announcements = response_data.get("data", [])
        if announcements:
            message = "📰 *Latest Public Service Announcements* 📰\n\n"
            for announcement in announcements[:5]:
                message += f" - {announcement.get('message', 'No message available')}\n"
            await update.message.reply_text(message, parse_mode="Markdown")
        else:
            await update.message.reply_text("No public service announcements available.")
    else:
        await update.message.reply_text(f"Failed to fetch announcements. Status: {status_code}")

async def fetch_histogram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display typing speed histogram."""
    endpoint = "/speed/histogram"
    status_code, response_data = fetch_from_api(endpoint, "")

    if status_code == 200:
        histogram_data = response_data.get("data", [])
        message = "📊 *Typing Speed Distribution* 📊\n\n"
        for entry in histogram_data:
            speed_range = entry.get("speedRange")
            count = entry.get("count")
            message += f" - {speed_range} WPM: {count} entries\n"
        await update.message.reply_text(message, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Failed to fetch histogram. Status: {status_code}")


def main():
    # Load Telegram bot token from environment variable
    telegram_bot_token = os.getenv("TELEGRAM_API_KEY")
    if not telegram_bot_token:
        print("Error: TELEGRAM_API_KEY is not set in the environment variables.")
        return

    application = ApplicationBuilder().token(telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setapikey", set_api_key))
    application.add_handler(CommandHandler("recentresult", recent_result))
    application.add_handler(CommandHandler("checkpersonalbest", check_personal_best))
    application.add_handler(CommandHandler("news", fetch_news))
    application.add_handler(CommandHandler("histogram", fetch_histogram))
    application.run_polling()

if __name__ == "__main__":
    main()
