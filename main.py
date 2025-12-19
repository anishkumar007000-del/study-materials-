import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

# 🔐 Admin Telegram ID (apna ID daalo)
ADMIN_ID = 7241259696  

user_class = {}
pending_upload = {}  # admin upload state

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📘 Class 11", callback_data="class11")],
        [InlineKeyboardButton("📗 Class 10", callback_data="class10")]
    ]
    await update.message.reply_text(
        "Welcome 📚\nApni class choose karo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- CLASS SELECT ----------------
async def class_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    class_name = query.data
    user_class[query.from_user.id] = class_name

    if class_name == "class9":
        subjects = ["maths", "physics", "chemistry", "biology"]
    else:
        subjects = ["maths", "physics", "chemistry", "biology",]

    keyboard = [
        [InlineKeyboardButton(sub.capitalize(), callback_data=f"sub_{sub}")]
        for sub in subjects
    ]

    await query.edit_message_text(
        f"✅ {class_name.upper()} selected\nSubject choose karo:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- SEND PDF ----------------
async def subject_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    subject = query.data.replace("sub_", "")
    uid = query.from_user.id

    if uid not in user_class:
        await query.message.reply_text("❗ Pehle class select karo")
        return

    cls = user_class[uid]
    path = f"materials/{cls}/{subject}.pdf"

    if not os.path.exists(path):
        await query.message.reply_text("❌ PDF available nahi hai")
        return

    await query.message.reply_document(
        document=open(path, "rb"),
        caption=f"{cls.upper()} - {subject.upper()}"
    )

# ======================================================
# 2️⃣ ADMIN-ONLY PDF UPLOAD
# ======================================================

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "PDF bhejo with caption:\n\n"
        "`class9 maths`\n`class10 physics`",
        parse_mode="Markdown"
    )
    pending_upload[update.effective_user.id] = True

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid != ADMIN_ID or uid not in pending_upload:
        return

    caption = update.message.caption
    if not caption:
        await update.message.reply_text("❌ Caption missing")
        return

    cls, subject = caption.split()
    folder = f"materials/{cls}"
    os.makedirs(folder, exist_ok=True)

    file = await update.message.document.get_file()
    path = f"{folder}/{subject}.pdf"
    await file.download_to_drive(path)

    pending_upload.pop(uid)
    await update.message.reply_text("✅ PDF uploaded successfully")

# ---------------- APP ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("upload", upload))

app.add_handler(CallbackQueryHandler(class_select, pattern="^class"))
app.add_handler(CallbackQueryHandler(subject_select, pattern="^sub_"))

app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

print("Bot running with buttons + admin upload...")
app.run_polling()

