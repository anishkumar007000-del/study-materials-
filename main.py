import os
import json
import time
from telegram import *
from telegram.ext import *

# ==========================================================
# CONFIG
# ==========================================================
BOT_TOKEN = "YOUR_BOT_TOKEN"     # <-- APNA NEW TOKEN DALNA

ADMIN_ID = 7241259696            # SIRF ADMIN ACCESS
DB_FILE = "db.json"              # SHORTLINK + PDF DATABASE
PDF_DIR = "pdfs"                 # PDFs Folder

# ==========================================================
# DATABASE LOAD / SAVE
# ==========================================================
def load_db():
    if not os.path.exists(DB_FILE):
        return {"data": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

db = load_db()


# ==========================================================
# START COMMAND
# ==========================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📘 Class 9", callback_data="class_9")],
        [InlineKeyboardButton("📗 Class 10", callback_data="class_10")],
        [InlineKeyboardButton("📕 Class 11", callback_data="class_11")],
        [InlineKeyboardButton("📙 Class 12", callback_data="class_12")],
    ]

    await update.message.reply_text(
        "🎓 *WELCOME TO STUDY MATERIAL BOT*\n\n"
        "📚 NCERT + Modules + Notes\n"
        "👇 Choose Your Class",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================================
# CLASS SELECT
# ==========================================================
async def class_select(update, context):
    q = update.callback_query
    await q.answer()

    class_no = q.data.split("_")[1]
    q.from_user.class_no = class_no

    if class_no not in db["data"]:
        db["data"][class_no] = {}
        save_db(db)

    subjects = list(db["data"][class_no].keys())

    keyboard = []
    for s in subjects:
        keyboard.append([InlineKeyboardButton(s, callback_data=f"sub_{s}")])

    keyboard.append([InlineKeyboardButton("🏠 Home", callback_data="go_home")])

    await q.message.edit_text(
        f"📘 *Class {class_no}*\n\nChoose Subject 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================================
# SUBJECT SELECT
# ==========================================================
async def subject_select(update, context):
    q = update.callback_query
    await q.answer()

    subject = q.data.replace("sub_", "")

    context.user_data["class"] = q.from_user.class_no
    context.user_data["subject"] = subject
    context.user_data["time"] = int(time.time())

    keyboard = [
        [InlineKeyboardButton("🔗 OPEN LINK", url=db["data"][q.from_user.class_no][subject]["shortlink"])],
        [InlineKeyboardButton("✅ VERIFY", callback_data="verify")],
        [InlineKeyboardButton("🏠 Home", callback_data="go_home")],
    ]

    await q.message.edit_text(
        f"📂 *{subject} – Verification Required*\n\n"
        "1️⃣ Click the link\n"
        "2️⃣ Complete steps\n"
        "3️⃣ Press VERIFY",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================================
# VERIFY
# ==========================================================
async def verify(update, context):
    q = update.callback_query
    await q.answer()

    class_no = context.user_data.get("class")
    subject = context.user_data.get("subject")
    verify_time = context.user_data.get("time")

    if not class_no or not subject:
        return await q.message.reply_text("❌ Session expired! Try again.")

    if int(time.time()) - verify_time < 10:
        return await q.message.reply_text("⏳ Please wait 10 sec after opening link!")

    pdf_path = db["data"][class_no][subject]["path"]

    if not os.path.exists(pdf_path):
        return await q.message.reply_text("❌ PDF missing on server!")

    await q.message.reply_text("📤 Sending PDF...")

    await context.bot.send_document(
        chat_id=q.from_user.id,
        document=open(pdf_path, "rb"),
        caption=f"📘 Class {class_no} – {subject}"
    )


# ==========================================================
# ADMIN PANEL
# ==========================================================
async def admin(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Access Denied!")

    keyboard = [
        [InlineKeyboardButton("➕ Add Subject", callback_data="admin_add")],
        [InlineKeyboardButton("🗑 Remove Subject", callback_data="admin_remove")],
        [InlineKeyboardButton("📄 List All", callback_data="admin_list")],
    ]

    await update.message.reply_text(
        "👑 *Admin Panel*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==========================================================
# ADMIN BUTTONS
# ==========================================================
admin_state = {}

async def admin_buttons(update, context):
    q = update.callback_query
    await q.answer()

    if q.from_user.id != ADMIN_ID:
        return await q.message.reply_text("❌ Access Denied!")

    if q.data == "admin_add":
        admin_state["mode"] = "add_class"
        return await q.message.reply_text("Send Class Number (9/10/11/12):")

    if q.data == "admin_remove":
        admin_state["mode"] = "remove_sub"
        return await q.message.reply_text("Send key (e.g. `11_Physics`):", parse_mode="Markdown")

    if q.data == "admin_list":
        msg = "📄 *Available Data:*\n\n"
        for c in db["data"]:
            for s in db["data"][c]:
                msg += f"✔ `{c}_{s}`\n"
        return await q.message.reply_text(msg, parse_mode="Markdown")


# ==========================================================
# ADMIN MESSAGE HANDLER
# ==========================================================
async def admin_message(update, context):
    uid = update.message.from_user.id
    if uid != ADMIN_ID:
        return

    msg = update.message.text

    # ========== ADD SUBJECT ==========
    if admin_state.get("mode") == "add_class":
        admin_state["class"] = msg
        admin_state["mode"] = "add_subject"
        return await update.message.reply_text("Enter Subject Name:")

    if admin_state.get("mode") == "add_subject":
        admin_state["subject"] = msg
        admin_state["mode"] = "add_short"
        return await update.message.reply_text("Enter Shortlink URL:")

    if admin_state.get("mode") == "add_short":
        admin_state["shortlink"] = msg
        admin_state["mode"] = "add_path"
        return await update.message.reply_text("Enter PDF PATH (inside pdfs/):")

    if admin_state.get("mode") == "add_path":
        class_no = admin_state["class"]
        subject = admin_state["subject"]
        shortlink = admin_state["shortlink"]
        pdf_path = msg

        if class_no not in db["data"]:
            db["data"][class_no] = {}

        db["data"][class_no][subject] = {
            "path": pdf_path,
            "shortlink": shortlink
        }

        save_db(db)

        admin_state.clear()

        return await update.message.reply_text("✅ Subject Added Successfully!")

    # ========== REMOVE SUBJECT ==========
    if admin_state.get("mode") == "remove_sub":
        key = msg.split("_")    # example: 11_Physics
        class_no = key[0]
        subject = key[1]

        try:
            del db["data"][class_no][subject]
            save_db(db)
            admin_state.clear()
            return await update.message.reply_text("🗑 Removed Successfully!")
        except:
            return await update.message.reply_text("❌ Not Found!")



# ==========================================================
# MAIN MENU
# ==========================================================
async def go_home(update, context):
    if update.callback_query:
        return await start(update.callback_query, context)


# ==========================================================
# RUN BOT
# ==========================================================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))

app.add_handler(CallbackQueryHandler(class_select, pattern="^class_"))
app.add_handler(CallbackQueryHandler(subject_select, pattern="^sub_"))
app.add_handler(CallbackQueryHandler(go_home, pattern="go_home"))
app.add_handler(CallbackQueryHandler(admin_buttons, pattern="admin_"))
app.add_handler(CallbackQueryHandler(verify, pattern="verify"))

app.add_handler(MessageHandler(filters.TEXT, admin_message))

print("🔥 STUDY BOT READY!")
app.run_polling()
