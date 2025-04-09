from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re

# Dictionary to track user offenses
user_offenses = {}

# Maximum number of allowed offenses before banning a user
MAX_OFFENSES = 2

# Function to check for URLs
def contains_url(text):
    # Regex to detect HTTP/HTTPS URLs and links starting with "www."
    url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}"
    return re.search(url_pattern, text)

def contains_text_link(mes):
    typ = False
    for entity in mes.entities:
        typ = entity.type == "text_link" or entity.type == "mention"
    return typ

def contains__links(text: str) -> bool:
    telegram_user_pattern = r"(?:@[\w\d_]{5,32}|https?://(?:www\.)?t\.me/(?:[\w\d_]{5,32}|\+[\w\d]+)|t\.me/(?:[\w\d_]{5,32}|\+[\w\d]+))"
    return re.search(telegram_user_pattern, text.lower()) is not None

async def filter_ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    text = message.text or message.caption or ""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Check if message contains links or banned keywords
    if contains__links(text) or contains_url(text)  or contains_text_link(message): # or any(keyword in text for keyword in BANNED_KEYWORDS):
        # Delete the message containing ads or links
        await message.delete()

        # Track offenses for the user
        user_offenses[user_id] = user_offenses.get(user_id, 0) + 1
        offense_count = user_offenses[user_id]

        # If the user has exceeded the max allowed offenses, ban them
        if offense_count >= MAX_OFFENSES:
            await context.bot.ban_chat_member(chat_id, user_id)
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🚫 User @{message.from_user.username or message.from_user.first_name} has been banned for repeated spamming and advertising."
            )
        else:
            # Notify the user about the offense
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ @{message.from_user.username or message.from_user.first_name}, stop advertising! (Warning {offense_count}/{MAX_OFFENSES})"
            )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am an anti-spam bot. I will block ads and links in this group.")

def main():
    print("Working")
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token("7896001334:AAFq21moEI60YC3ZmO2d12i3p-Z_ofPoTSc").build()

    # Add command and message handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_ads))
    # Listen to messages with text or photos
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, filter_ads))
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
