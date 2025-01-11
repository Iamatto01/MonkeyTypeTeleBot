import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# API keys
MONKEYTYPE_API_KEY = "YOUR_MONKEYTYPE_API_KEY"
TELEGRAM_API_KEY = "YOUR_TELEGRAM_API_KEY"

# Base Monkeytype API URL
MONKEYTYPE_API_BASE = "https://api.monkeytype.com"

# Utility function to fetch data from Monkeytype API
def fetch_from_api(endpoint: str, headers=None, params=None):
    try:
        url = f"{MONKEYTYPE_API_BASE}{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    welcome_message = (
        "Welcome to the Monkeytype Tracker Bot! 🎉\n\n"
        "Available commands:\n"
        "/recentresult - View your most recent typing test\n"
        "/checkpersonalbest - View your personal best stats\n"
        "/typingstats - View global typing stats\n"
    )
    await update.message.reply_text(welcome_message)

async def recent_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display the user's most recent result."""
    endpoint = "/results/last"
    headers = {"Authorization": f"ApeKey {MONKEYTYPE_API_KEY}"}
    status_code, response_data = fetch_from_api(endpoint, headers=headers)

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
    """Fetch and display the user's personal bests for different durations and word counts."""
    endpoint = "/results"
    headers = {"Authorization": f"ApeKey {MONKEYTYPE_API_KEY}"}
    params = {"limit": 1000}  # Fetch a larger dataset to analyze personal bests
    status_code, response_data = fetch_from_api(endpoint, headers=headers, params=params)

    if status_code == 200:
        results = response_data.get("data", [])
        # Initialize personal bests for each category
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

        # Analyze results to find the highest WPM for each category
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

        # Create the message with personal bests
        pb_message = "🏆 *Your Personal Bests* 🏆\n\n"
        for category, wpm in categories.items():
            pb_message += f" - {category}: {wpm if wpm else 'No data available'} WPM\n"

        await update.message.reply_text(pb_message, parse_mode="Markdown")
    elif status_code == 401:
        await update.message.reply_text("Authentication error. Please check your API key.")
    else:
        await update.message.reply_text(f"Failed to fetch personal bests. Status: {status_code}")

async def typing_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display global typing stats."""
    endpoint = "/public/typingStats"
    status_code, response_data = fetch_from_api(endpoint)

    if status_code == 200:
        data = response_data.get("data", {})
        stats_message = (
            "🌎 *Global Typing Stats* 🌎\n\n"
            f" - Total Time Typed: {data.get('timeTyping')} hours\n"
            f" - Tests Completed: {data.get('testsCompleted')} tests\n"
        )
        await update.message.reply_text(stats_message, parse_mode="Markdown")
    else:
        await update.message.reply_text(f"Failed to fetch typing stats. Status: {status_code}")

def main():
    # Create the Telegram bot application
    application = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("recentresult", recent_result))
    application.add_handler(CommandHandler("checkpersonalbest", check_personal_best))
    application.add_handler(CommandHandler("typingstats", typing_stats))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
