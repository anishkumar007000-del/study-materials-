import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIG =================
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set")

# Study material data
STUDY_MATERIAL = {
    "Math": {
        "Algebra": "https://example.com/algebra.pdf",
        "Geometry": "https://example.com/geometry.pdf",
    },
    "Science": {
        "Physics": "https://example.com/physics.pdf",
        "Chemistry": "https://example.com/chemistry.pdf",
    },
    "Computer": {
        "Python": "https://example.com/python.pdf",
        "HTML": "https://example.com/html.pdf",
    },
}

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Welcome to Study Material Bot!*\n\n"
        "👉 Use /subjects to get study material\n"
        "👉 Use /help for commands",
        parse_mode="Markdown",
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *Help Menu*\n\n"
        "/start - Start the bot\n"
        "/subjects - Browse subjects\n"
        "/about - About this bot",
        parse_mode="Markdown",
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Study Material Bot*\n"
        "Simple • Fast • Student Friendly",
        parse_mode="Markdown",
    )

async def subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(subject, callback_data=f"subject:{subject}")]
        for subject in STUDY_MATERIAL
    ]

    await update.message.reply_text(
        "📖 *Choose a subject:*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# ================= BUTTON HANDLER =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("subject:"):
        subject = data.split(":")[1]

        keyboard = [
            [InlineKeyboardButton(topic, callback_data=f"topic:{subject}:{topic}")]
            for topic in STUDY_MATERIAL[subject]
        ]

        await query.edit_message_text(
            f"📘 *{subject} Topics:*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    elif data.startswith("topic:"):
        _, subject, topic = data.split(":")
        link = STUDY_MATERIAL[subject][topic]

        await query.edit_message_text(
            f"📄 *{topic}*\n\n"
            f"👉 [Download Material]({link})",
            parse_mode="Markdown",
        )

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("subjects", subjects))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

