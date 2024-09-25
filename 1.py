import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from datetime import datetime, time
import pytz
import random

# Replace 'YOUR_TOKEN' with your actual bot token
TOKEN = '7008610078:AAFaJCtmTJI9mMf_uN3KvlYtfY5ion7IrHM'

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Dictionary to store the state of predictions and user states
predictions = {}
user_states = {}

# Required channels
REQUIRED_CHANNELS = ["@bitgit_official"]

# Time windows for predictions
TIME_WINDOWS = [
    (time(8, 30), time(9, 30)),
    (time(11, 0), time(12, 0)),
    (time(14, 0), time(15, 0)),
    (time(17, 0), time(18, 0))
]

# Create the main menu keyboard
def get_main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📈Trend Chart📉"), KeyboardButton("Prediction🎲")],
            [KeyboardButton("🚀Main Channel"), KeyboardButton("📩Customer Support")]
        ],
        resize_keyboard=True  # Resize keyboard to fit the buttons
    )

# Generate the period and result
def generate_prediction(period_number):
    if period_number not in predictions:
        result = random.choice(["Red", "Green"])
        predictions[period_number] = result
    return predictions[period_number]

# Get the current period number
def get_current_period():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    period_date = now.strftime('%Y%m%d')  # yyyyMMdd format
    total_minutes = now.hour * 60 + now.minute + 1  # Current hours * 60 + current minutes + 1
    period_number = f"{total_minutes:04d}"  # Ensure the period number is exactly 4 digits
    return f"{period_date}{period_number}"

# Check if the user has joined the required channels
async def is_user_in_channels(user_id: int, bot) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            member_status = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member_status.status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

# Check if the current time is within the allowed prediction time windows
def is_within_time_window():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz).time()
    for start, end in TIME_WINDOWS:
        if start <= now <= end:
            return True
    return False

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.message.from_user.id
    if user_id not in user_states:
        user_states[user_id] = {'joined': False, 'verified': False}

    join_buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Join Channel", url=f"https://t.me/{REQUIRED_CHANNELS[0][1:]}")]
        ]
    )
    await update.message.reply_text(
        '*You must join our Telegram channel to use this bot. Please join the channel below and then use /verify to verify your membership.*',
        reply_markup=join_buttons,
        parse_mode='Markdown'
    )

# Verify command
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Verify if the user has joined the channels."""
    user_id = update.message.from_user.id

    if await is_user_in_channels(user_id, context.bot):
        user_states[user_id]['verified'] = True
        keyboard = get_main_menu_keyboard()
        await update.message.reply_text(
            '*Verification complete! You can now use the bot. Please choose an option:*',
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            '*Verification failed! You need to join the channel first.*',
            parse_mode='Markdown'
        )

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle messages sent by the user."""
    user_id = update.message.from_user.id

    if user_id not in user_states or not user_states[user_id]['verified']:
        await update.message.reply_text(
            "*You need to verify your membership first. Use /verify to complete verification.*",
            parse_mode='Markdown'
        )
        return

    text = update.message.text

    if text == "📈Trend Chart📉":
        trend_chart_message = """
*📈 All Games Trend
💹 Max Rate: 88%

✔️ Red = 🔴
✔️ Green = 🟢

🚀 Basic trends 🔥
────────────
1. 🔴🟢🔴🟢🔴🟢
────────────
2. 🔴🔴🟢🟢🔴🔴
────────────
3. 🔴🔴🔴🟢🟢🟢
────────────
4. 🟢🟢🟢🟢🔴🔴🔴🔴
────────────
5. 🟢🟢🟢🟢🟢🟢
────────────
6. 🔴🔴🔴🔴🔴🔴
────────────

📈 IN Game trends 🚀
────────────
1. 🟢🔴🟢🔴🟢🟢🔴
────────────
2. 🔴🟢🟢🟢🔴🔴🟢
────────────
3. 🟢🟢🟢🔴🟢🟢🟢🔴
────────────
4. 🔴🔴🟢🟢🔴🟢🟢
────────────
5. 🟢🟢🔴🔴🟢🟢🟢🔴🔴
────────────
6. 🔴🔴🔴🔴🔴🟢🔴
────────────
7. 🟢🟢🟢🟢🟢🔴🟢
────────────
8. 🔴🔴🔴🟢🔴🔴🔴
────────────

🚀 Get accurate predictions for the next game! with all our features given to us for win !
📩*
        """
        await update.message.reply_text(trend_chart_message, parse_mode='Markdown')
    elif text == "Prediction🎲":
        if is_within_time_window():
            period_number = get_current_period()  # Get current period number
            result = generate_prediction(period_number)  # Generate or retrieve prediction
            game_result = f"*1-minute Server\n\n🔰Game Period : {period_number}\n👉Game Result : {result}*"
            await update.message.reply_text(game_result, parse_mode='Markdown')  # Show the result immediately
        else:
            await update.message.reply_text(
                "🤖🔴🚫 *The bot is currently not live. It will be live at*\n\n"
                "⏰ 08:30 AM - 09:30 AM\n"
                "⏰ 11:00 AM - 12:00 PM\n"
                "⏰ 02:00 PM - 03:00 PM\n"
                "⏰ 05:00 PM - 06:00 PM\n\n"
                "These timings provide maximum signal accuracy up to 95% for stable profit. Manage minimum 6 levels🎯",
                parse_mode='Markdown'
            )
    elif text == "🚀Main Channel":
        channel_message = (
            "*Here is our main channel:*\n"
            f"[@bitgit_official](https://t.me/{REQUIRED_CHANNELS[0][1:]})"
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Join Channel", url=f"https://t.me/{REQUIRED_CHANNELS[0][1:]}")]
            ]
        )
        await update.message.reply_text(channel_message, reply_markup=keyboard, parse_mode='Markdown')
    elif text == "📩Customer Support":
        owner_contact_message = (
            "*Here is the owner of the bot:*\n"
            "*[@rahul_mods67](https://t.me/rahul_mods67)*"
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Contact Owner", url="https://t.me/rahul_mods67")]
            ]
        )
        await update.message.reply_text(owner_contact_message, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.message.reply_text("*Please choose an option from the keyboard.*", parse_mode='Markdown')

def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Notify that the bot is running
    logging.info("Bot is running...")

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
