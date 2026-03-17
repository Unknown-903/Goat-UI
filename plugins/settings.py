import os
import sys
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper.database import codeflixbots as db
from helper.auth import auth_chats
from helper.permissions import is_admin as _perm_is_admin
from config import Config

logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

# ================= ADMIN CHECK =================

def is_admin(user_id):
    return user_id == Config.OWNER_ID or _perm_is_admin(user_id)

# ================= STATE =================
# Waiting for user input
settings_state = {}  # user_id -> "thumb" | "meta"

# ================= MENUS =================

def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼️  Thumbnail", callback_data="stg|thumb_menu"),
            InlineKeyboardButton("🏷️  Metadata",  callback_data="stg|meta_menu"),
        ],
        [
            InlineKeyboardButton("❌  Close", callback_data="stg|close"),
        ]
    ])

async def thumb_menu(user_id):
    thumb = await db.get_thumbnail(user_id)
    status = "✅ Set" if thumb else "❌ Not set"
    buttons = [
        [InlineKeyboardButton(f"📊 Status: {status}", callback_data="stg|noop")],
    ]
    if thumb:
        buttons.append([
            InlineKeyboardButton("👁️  View",   callback_data="stg|thumb_view"),
            InlineKeyboardButton("🗑️  Delete", callback_data="stg|thumb_del"),
        ])
    buttons.append([InlineKeyboardButton("📸  Upload New Thumbnail", callback_data="stg|thumb_set")])
    buttons.append([InlineKeyboardButton("🔙  Back", callback_data="stg|back")])
    return InlineKeyboardMarkup(buttons)

async def meta_menu(user_id):
    title  = await db.get_title(user_id)
    author = await db.get_author(user_id)
    artist = await db.get_artist(user_id)
    val = title or author or artist
    status = f"✅ `{val}`" if val else "❌ Not set"
    buttons = [
        [InlineKeyboardButton(f"📊 Status: {title or 'Not set'}", callback_data="stg|noop")],
    ]
    if val:
        buttons.append([
            InlineKeyboardButton("👁️  View",   callback_data="stg|meta_view"),
            InlineKeyboardButton("🗑️  Delete", callback_data="stg|meta_del"),
        ])
    buttons.append([InlineKeyboardButton("✏️  Set Metadata", callback_data="stg|meta_set")])
    buttons.append([InlineKeyboardButton("🔙  Back", callback_data="stg|back")])
    return InlineKeyboardMarkup(buttons)

# ================= /settings COMMAND =================

@Client.on_message(
    (filters.private | filters.group) &
    filters.command("settings")
)
async def settings_cmd(client, message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.reply_text("❌ Sirf owner aur admins use kar sakte hain")
        return

    await message.reply_text(
        "⚙️ **Bot Settings**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🖼️  **Thumbnail** — Custom thumbnail for uploads\n"
        "🏷️  **Metadata** — Title, Author & Artist tags\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=main_menu()
    )

# ================= CALLBACK ROUTER =================

@Client.on_callback_query(filters.regex("^stg[|]"))
async def settings_cb(client, query: CallbackQuery):
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("❌ Access denied!", show_alert=True)
        return

    action = query.data.split("|")[1]

    # -------- NOOP --------
    if action == "noop":
        await query.answer()
        return

    # -------- CLOSE --------
    elif action == "close":
        await query.message.delete()
        return

    # -------- BACK --------
    elif action == "back":
        settings_state.pop(user_id, None)
        await query.message.edit_text(
            "⚙️ **Bot Settings**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🖼️  **Thumbnail** — Custom thumbnail for uploads\n"
            "🏷️  **Metadata** — Title, Author & Artist tags\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=main_menu()
        )

    # ======== THUMBNAIL ========

    elif action == "thumb_menu":
        await query.message.edit_text(
            "🖼️ **Thumbnail Settings**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Set a custom thumbnail that will be used\n"
            "for all your file uploads.\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=await thumb_menu(user_id)
        )

    elif action == "thumb_view":
        thumb = await db.get_thumbnail(user_id)
        if thumb:
            await client.send_photo(
                chat_id=query.message.chat.id,
                photo=thumb,
                caption="🖼️ **Your current thumbnail**"
            )
            await query.answer("✅ Thumbnail sent!")
        else:
            await query.answer("❌ No thumbnail set!", show_alert=True)

    elif action == "thumb_del":
        await db.set_thumbnail(user_id, None)
        await query.answer("🗑️ Thumbnail deleted!")
        await query.message.edit_text(
            "🖼️ **Thumbnail Settings**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Set a custom thumbnail that will be used\n"
            "for all your file uploads.\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=await thumb_menu(user_id)
        )

    elif action == "thumb_set":
        settings_state[user_id] = "thumb"
        await query.message.edit_text(
            "🖼️ **Upload Thumbnail**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📸 Ab koi bhi **photo** bhejo\n"
            "Bot automatically thumbnail set kar dega\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Cancel karne ke liye /settings bhejo",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌  Cancel", callback_data="stg|back")]
            ])
        )

    # ======== METADATA ========

    elif action == "meta_menu":
        await query.message.edit_text(
            "🏷️ **Metadata Settings**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Set Title, Author & Artist tags\n"
            "for all encoded/compressed files.\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=await meta_menu(user_id)
        )

    elif action == "meta_view":
        title  = await db.get_title(user_id)
        author = await db.get_author(user_id)
        artist = await db.get_artist(user_id)
        await query.message.edit_text(
            "🏷️ **Current Metadata**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📌 Title  : `{title  or 'Not Set'}`\n"
            f"✍️ Author : `{author or 'Not Set'}`\n"
            f"🎨 Artist : `{artist or 'Not Set'}`\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙  Back", callback_data="stg|meta_menu")]
            ])
        )

    elif action == "meta_del":
        await db.set_title(user_id, "")
        await db.set_author(user_id, "")
        await db.set_artist(user_id, "")
        await query.answer("🗑️ Metadata deleted!")
        await query.message.edit_text(
            "🏷️ **Metadata Settings**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Set Title, Author & Artist tags\n"
            "for all encoded/compressed files.\n\n"
            "━━━━━━━━━━━━━━━━━━━━",
            reply_markup=await meta_menu(user_id)
        )

    elif action == "meta_set":
        settings_state[user_id] = "meta"
        await query.message.edit_text(
            "🏷️ **Set Metadata**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "✏️ Ab apna **naam** bhejo\n"
            "Example: `SharkToonsIndia`\n\n"
            "Yeh Title, Author & Artist\n"
            "teeno mein set ho jayega\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Cancel karne ke liye /settings bhejo",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌  Cancel", callback_data="stg|back")]
            ])
        )

# ================= CAPTURE USER INPUT =================

@Client.on_message(
    (filters.private | filters.group) &
    filters.text &
    ~filters.command(["settings", "start", "help", "encode", "compress",
                      "merge", "done", "mergecancel", "upscale", "select",
                      "queue", "logs", "restart", "status", "add", "rm", "addlist"]),
    group=2
)
async def settings_input(client, message):
    user_id = message.from_user.id
    state = settings_state.get(user_id)
    if not state:
        return

    # -------- METADATA INPUT --------
    if state == "meta":
        name = message.text.strip()
        if not name:
            await message.reply_text("❌ Empty naam — phir try karo")
            return

        await db.set_title(user_id, name)
        await db.set_author(user_id, name)
        await db.set_artist(user_id, name)
        settings_state.pop(user_id, None)

        await message.reply_text(
            f"✅ **Metadata saved!**\n\n"
            f"📌 Title  : `{name}`\n"
            f"✍️ Author : `{name}`\n"
            f"🎨 Artist : `{name}`\n\n"
            f"Use /settings to manage",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️  Open Settings", callback_data="stg|meta_menu")]
            ])
        )

# ================= CAPTURE PHOTO FOR THUMB =================

@Client.on_message(
    (filters.private | filters.group) &
    filters.photo,
    group=2
)
async def settings_thumb_input(client, message):
    user_id = message.from_user.id
    state = settings_state.get(user_id)
    if state != "thumb":
        return

    file_id = message.photo.file_id
    await db.set_thumbnail(user_id, file_id)
    settings_state.pop(user_id, None)

    await message.reply_text(
        "✅ **Thumbnail saved!**\n\n"
        "Yeh thumbnail ab sab uploads mein use hoga\n\n"
        "Use /settings to manage",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚙️  Open Settings", callback_data="stg|thumb_menu")]
        ])
    )
