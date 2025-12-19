import os, time
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ===========================================
# CONFIG
# ===========================================
BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"

ADMIN_ID = 7241259696
WELCOME_IMAGE = "https://t.me/BG_materials_og/2"

# ===========================================
CLASSES = ["9", "10", "11", "12"]

SUBJECTS = {
    "9": ["Physics", "Chemistry", "Biology", "Maths", "Hindi", "English", "Social"],
    "10": ["Physics", "Chemistry", "Biology", "Maths", "Hindi", "English", "Social"],
    "11": ["Physics", "Chemistry", "Biology", "Maths", "English"],
    "12": ["Physics", "Chemistry", "Biology", "Maths", "English"],
}

# PDF DATABASE
PDF_FILES = {
    "9_Physics": "pdfs/9_Physics.pdf",
    "10_Maths": "pdfs/10_Maths.pdf",
    "11_Physics": "pdfs/11_Physics.pdf",
}

user_state = {}
admin_state = {}

# ===========================================
# MAIN KEYBOARD
# ===========================================
MAIN_REPLY_KEYBOARD = ReplyKeyboardMarkup(
    [
        ["👑 OWNER", "📚 NCERT"],
        ["🧩 MODULES", "📘 MTG"],
        ["📖 DISHA", "✏️ KVPY"],
        ["🧠 VEDANTU", "⚡ BYJU'S"],
        ["📕 ARIHANT", "🚀 PW"]
    ],
    resize_keyboard=True
)

# ===========================================
async def safe_edit(query, text, keyboard):
    try:
        await query.edit_message_caption(
            caption=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except:
        await query.edit_message_text(
            text=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# ===========================================
# START
# ===========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = (
        "🎓 *WELCOME TO CLASS DECODE BOT*\n\n"
        "📚 NCERT Full Books\n"
        "🧩 Modules & PYQs\n"
        "📝 Short Notes & Mindmaps\n"
        "⚡ High Quality Content\n\n"
        "👇 *Choose your class to continue*"
    )

    keyboard = [
        [
            InlineKeyboardButton("📘 Class 9", callback_data="class_9"),
            InlineKeyboardButton("📗 Class 10", callback_data="class_10")
        ],
        [
            InlineKeyboardButton("📕 Class 11", callback_data="class_11"),
            InlineKeyboardButton("📙 Class 12", callback_data="class_12")
        ]
    ]

    if update.message:
        await update.message.reply_photo(
            photo=WELCOME_IMAGE,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ===========================================
# CLASS SELECT
# ===========================================
async def class_select(update, context):
    q = update.callback_query
    await q.answer()

    class_no = q.data.split("_")[1]
    user_state[q.from_user.id] = {"class": class_no}

    subs = SUBJECTS[class_no]
    keyboard = []

    for i in range(0, len(subs), 2):
        row = [InlineKeyboardButton(subs[i], callback_data=f"sub_{subs[i]}")]
        if i + 1 < len(subs):
            row.append(InlineKeyboardButton(subs[i+1], callback_data=f"sub_{subs[i+1]}"))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton("⬅️ Back", callback_data="go_start"),
        InlineKeyboardButton("🏠 Main Menu", callback_data="go_start")
    ])

    await safe_edit(
        q,
        f"📘 *Class {class_no}*\n\nSelect Subject 👇",
        InlineKeyboardMarkup(keyboard)
    )

# ===========================================
# SUBJECT SELECT
# ===========================================
async def subject_select(update, context):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    subject = q.data.replace("sub_", "")
    class_no = user_state[uid]["class"]

    user_state[uid].update({
        "subject": subject,
        "token_time": int(time.time())
    })

    keyboard = [
        [InlineKeyboardButton("🔗 Get Access Link", callback_data="getlink")],
        [
            InlineKeyboardButton("⬅️ Back", callback_data=f"class_{class_no}"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="go_start")
        ]
    ]

    await safe_edit(
        q,
        f"📂 *Class {class_no} – {subject}*\n\n"
        "🔐 Verification Required",
        InlineKeyboardMarkup(keyboard)
    )

# ===========================================
# GET LINK
# ===========================================
async def get_link(update, context):
    q = update.callback_query
    await q.answer()

    keyboard = [
        [InlineKeyboardButton("✅ Verify", callback_data="verify")],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="go_start"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="go_start")
        ]
    ]

    await safe_edit(
        q,
        "🔗 *Access Link Generated*\n\n"
        "👉 Complete ads\n"
        "👉 Then click **Verify**",
        InlineKeyboardMarkup(keyboard)
    )

# ===========================================
# VERIFY
# ===========================================
async def verify(update, context):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    data = user_state.get(uid)

    if not data:
        await q.message.reply_text("❌ Session expired")
        return

    key = f"{data['class']}_{data['subject']}"
    pdf_path = PDF_FILES.get(key)

    if not pdf_path or not os.path.exists(pdf_path):
        await q.message.reply_text("✅ Verified!\n\n📘 PDF: https://drive.google.com/xxxxx")
        return

    await q.message.reply_text("📤 Sending file...")
    
    try:
        await context.bot.send_document(
            chat_id=uid,
            document=open(pdf_path, 'rb'),
            caption=f"📘 Class {data['class']} – {data['subject']}"
        )
    except Exception as e:
        await q.message.reply_text(f"✅ Verified! File link: https://drive.google.com/xxxxx")

# ===========================================
# ADMIN PANEL
# ===========================================
async def admin(update, context):
    if update.message.from_user.id != ADMIN_ID:
        return await update.message.reply_text("❌ Access Denied")

    keyboard = [
        [InlineKeyboardButton("📁 Add PDF", callback_data="admin_add")],
        [InlineKeyboardButton("🗑 Remove PDF", callback_data="admin_remove")],
        [InlineKeyboardButton("📄 List PDFs", callback_data="admin_list")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_bc")]
    ]

    await update.message.reply_text(
        "👑 *Admin Panel*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===========================================
async def admin_buttons(update, context):
    q = update.callback_query
    await q.answer()

    uid = q.from_user.id
    if uid != ADMIN_ID:
        return await q.message.reply_text("❌ Access Denied")

    if q.data == "admin_add":
        admin_state[uid] = "await_class"
        await q.message.reply_text("➕ Send class (e.g. 9)")

    elif q.data == "admin_remove":
        admin_state[uid] = "remove_key"
        await q.message.reply_text("🗑 Send PDF key to remove (e.g. `9_Physics`)")

    elif q.data == "admin_list":
        msg = "📄 *Available PDFs:*\n\n"
        for k in PDF_FILES:
            msg += f"• `{k}` → {PDF_FILES[k]}\n"
        await q.message.reply_text(msg, parse_mode="Markdown")

    elif q.data == "admin_bc":
        admin_state[uid] = "broadcast"
        await q.message.reply_text("📢 Send broadcast message")

# ===========================================
async def admin_message(update, context):
    uid = update.message.from_user.id
    if uid != ADMIN_ID:
        return

    state = admin_state.get(uid)

    if state == "await_class":
        admin_state["class"] = update.message.text
        admin_state[uid] = "await_subject"
        return await update.message.reply_text("Subject name?")

    if state == "await_subject":
        admin_state["subject"] = update.message.text
        admin_state[uid] = "await_file"
        return await update.message.reply_text("PDF path? (local path)")

    if state == "await_file":
        class_no = admin_state["class"]
        subject = admin_state["subject"]
        path = update.message.text

        PDF_FILES[f"{class_no}_{subject}"] = path
        admin_state[uid] = None

        return await update.message.reply_text("✅ PDF Added Successfully!")

    if state == "remove_key":
        key = update.message.text
        if key in PDF_FILES:
            del PDF_FILES[key]
            await update.message.reply_text("🗑 Removed!")
        else:
            await update.message.reply_text("❌ Not Found")
        admin_state[uid] = None

    if state == "broadcast":
        text = update.message.text
        await update.message.reply_text("📢 Broadcasting...")

        # Broadcast to all users
        for user in user_state:
            try:
                await context.bot.send_message(chat_id=user, text=text)
            except:
                pass

        admin_state[uid] = None
        await update.message.reply_text("✅ Done!")

# ===========================================
async def go_start(update, context):
    if update.callback_query:
        await update.callback_query.message.delete()
    await start(update, context)

# ===========================================
# RUN BOT
# ===========================================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin))
app.add_handler(MessageHandler(filters.TEXT, admin_message))

app.add_handler(CallbackQueryHandler(admin_buttons, pattern="^admin_"))

app.add_handler(CallbackQueryHandler(class_select, pattern="^class_"))
app.add_handler(CallbackQueryHandler(subject_select, pattern="^sub_"))
app.add_handler(CallbackQueryHandler(get_link, pattern="^getlink$"))
app.add_handler(CallbackQueryHandler(verify, pattern="^verify$"))
app.add_handler(CallbackQueryHandler(go_start, pattern="^go_start$"))

print("🚀 BOT + ADMIN PANEL RUNNING...")
app.run_polling()
