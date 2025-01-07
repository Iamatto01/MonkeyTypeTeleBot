import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# API keys
MONKEYTYPE_API_KEY = ""
TELEGRAM_API_KEY = ""

# Base Monkeytype API URL
MONKEYTYPE_API_BASE = "https://api.monkeytype.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    welcome_message = (
        "Welcome to the Monkeytype Tracker Bot! 🎉\n\n"
        "Available commands:\n"
        "/personalbests - View your personal best stats\n"
        "/typingstats - View global typing stats\n"
    )
    await update.message.reply_text(welcome_message)


async def personal_bests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display the user's personal bests."""
    url = f"{MONKEYTYPE_API_BASE}/users/personalBests"
    headers = {"Authorization": f"Bearer {MONKEYTYPE_API_KEY}"}
    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    if response.status_code == 200:
        try:
            data = response.json()
            pb_message = "📈 *Your Personal Bests* 📈\n\n"
            for mode, stats in data.items():
                pb_message += f"*Mode:* {mode}\n"
                pb_message += f" - WPM: {stats['wpm']}\n"
                pb_message += f" - Accuracy: {stats['accuracy']}%\n"
                pb_message += f" - Consistency: {stats['consistency']}%\n\n"
            await update.message.reply_text(pb_message, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Error parsing data: {e}")
    else:
        await update.message.reply_text(f"Failed to fetch personal bests. Status: {response.status_code}")


async def typing_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display global typing stats."""
    url = f"{MONKEYTYPE_API_BASE}/public/typingStats"
    response = requests.get(url)

    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")

    if response.status_code == 200:
        try:
            data = response.json()
            stats_message = (
                "🌎 *Global Typing Stats* 🌎\n\n"
                f" - Total Time Typed: {data['totalTimeTyped']} hours\n"
                f" - Tests Completed: {data['testsCompleted']} tests\n"
            )
            await update.message.reply_text(stats_message, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Error parsing data: {e}")
    else:
        await update.message.reply_text(f"Failed to fetch typing stats. Status: {response.status_code}")


def main():
    # Create the Telegram bot application
    application = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("personalbests", personal_bests))
    application.add_handler(CommandHandler("typingstats", typing_stats))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
