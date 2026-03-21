import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from helper.database import codeflixbots
from config import Config


class Txt(object):

    START_TXT = """<b>⚡ G O A T  U I ⚡

━━━━━━━━━━━━━━━━━━━━
Hey {}! 👋

🤖 Advanced Media Processing Bot
━━━━━━━━━━━━━━━━━━━━

🎞 Encode　　•　🗜 Compress
🔀 Merge　　　•　🔬 Upscale
✏️ Rename　　•　⚙️ Settings

━━━━━━━━━━━━━━━━━━━━
Use /help to see all commands.</b>
"""

    HELP_TXT = """<b>📋 C O M M A N D S
━━━━━━━━━━━━━━━━━━━━

🎞 ENCODE
</b><code>/encode</code> — Reply to video → encode

<b>🗜 COMPRESS
</b><code>/compress</code> — Reply to video → compress

<b>🔀 MERGE
</b><code>/merge</code> — Start merge session
<code>/done</code> — Merge all files
<code>/mergecancel</code> — Cancel session

<b>🔬 UPSCALE
</b><code>/upscale</code> — Reply to image → upscale

<b>✏️ RENAME
</b><code>/autorename</code> — Set rename format
<code>/select 1-12</code> — Set episode range

<b>⚙️ SETTINGS
</b><code>/settings</code> — Thumbnail & Metadata

<b>📊 STATUS
</b><code>/status</code> — View all active tasks
━━━━━━━━━━━━━━━━━━━━</b>
"""

    FILE_NAME_TXT = """<b>✏️ A U T O  R E N A M E
━━━━━━━━━━━━━━━━━━━━
Set your format:
<code>/autorename Anime S{{season}}E{{episode}} {{quality}}</code>

Placeholders:
‣ <code>{{season}}</code>  — Season number
‣ <code>{{episode}}</code> — Episode number
‣ <code>{{quality}}</code> — Quality (1080p etc)

━━━━━━━━━━━━━━━━━━━━
Current Format: {format_template}</b>
"""

    PROGRESS_BAR = """
<b>» Size</b>  : {1} | {2}
<b>» Done</b>  : {0}%
<b>» Speed</b> : {3}/s
<b>» ETA</b>   : {4}
"""

    SEND_METADATA = """<b>🏷 M E T A D A T A
━━━━━━━━━━━━━━━━━━━━
Use /settings → 🏷 Metadata
to set Title, Author and Artist tags.</b>
"""

    THUMBNAIL_TXT = """<b>🖼 T H U M B N A I L  &  M E T A D A T A
━━━━━━━━━━━━━━━━━━━━
Use /settings to manage:
‣ 🖼 Thumbnail — upload custom thumb
‣ 🏷 Metadata — set title, author, artist</b>
"""

    DONATE_TXT = """<b>💝 S U P P O R T
━━━━━━━━━━━━━━━━━━━━
Enjoying the bot? Support us! ❤️

Every contribution keeps it running 🚀</b>
"""

    SOURCE_TXT = """<b>📦 S O U R C E
━━━━━━━━━━━━━━━━━━━━
This bot is a private project.

For support, contact the owner directly.</b>
"""

    ABOUT_TXT = """<b>ℹ️ A B O U T  B O T
━━━━━━━━━━━━━━━━━━━━

⚡ Goat UI — Advanced Media Bot

🎯 Features:
‣ 🎞 H.265 Video Encoding
‣ 🗜 Smart Compression
‣ 🔀 Multi-file Merging
‣ 🔬 AI Image Upscaling
‣ ✏️ Auto File Renaming
‣ ⚙️ Metadata & Thumbnail
‣ 📊 Live Task Status

━━━━━━━━━━━━━━━━━━━━
👨‍💻 Dev : @cosmic_freak
📢 Updates : @Codeflix_Bots</b>
"""

    CAPTION_TXT = ""


# ================= START =================

@Client.on_message(filters.command("start"))
async def start(client, message: Message):

    if message.chat.type in ["group", "supergroup"]:
        return await message.reply_text(
            "👋 **Hello!**\n\n"
            "Use me in **private chat** to rename files.\n\n"
            f"👉 https://t.me/{(await client.get_me()).username}"
        )

    user = message.from_user
    await codeflixbots.add_user(client, message)

    m = await message.reply_text("ʜᴇʜᴇ..ɪ'ᴍ ᴀɴʏᴀ!\nᴡᴀɪᴛ ᴀ ᴍᴏᴍᴇɴᴛ. . .")
    await asyncio.sleep(0.4)
    await m.edit_text("🎊")
    await asyncio.sleep(0.5)
    await m.edit_text("⚡")
    await asyncio.sleep(0.5)
    await m.edit_text("ᴡᴀᴋᴜ ᴡᴀᴋᴜ!...")
    await asyncio.sleep(0.4)
    await m.delete()

    await message.reply_sticker(
        "CAACAgUAAxkBAAECroBmQKMAAQ-Gw4nibWoj_pJou2vP1a4AAlQIAAIzDxlVkNBkTEb1Lc4eBA"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data="help")],
        [
            InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs", url="https://t.me/Codeflix_Bots"),
            InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ •", url="https://t.me/CodeflixSupport")
        ],
        [
            InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
            InlineKeyboardButton("sᴏᴜʀᴄᴇ •", callback_data="source")
        ]
    ])

    if Config.START_PIC:
        await message.reply_photo(
            Config.START_PIC,
            caption=Txt.START_TXT.format(user.mention),
            reply_markup=buttons
        )
    else:
        await message.reply_text(
            Txt.START_TXT.format(user.mention),
            reply_markup=buttons
        )


# ================= CALLBACK HANDLER =================

@Client.on_callback_query(filters.regex(r"^(home|help|settings_info|file_names|donate|about|source|close)$"))
async def cb_handler(client, query: CallbackQuery):

    data = query.data
    user_id = query.from_user.id

    if data == "home":

        await query.message.edit_text(
            Txt.START_TXT.format(query.from_user.mention),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴍʏ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs •", callback_data="help")],
                [
                    InlineKeyboardButton("• ᴜᴘᴅᴀᴛᴇs", url="https://t.me/Codeflix_Bots"),
                    InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ •", url="https://t.me/CodeflixSupport")
                ],
                [
                    InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("sᴏᴜʀᴄᴇ •", callback_data="source")
                ]
            ])
        )


    elif data == "help":

        bot = await client.get_me()

        await query.message.edit_text(
            Txt.HELP_TXT.format(bot.mention),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ •", callback_data="file_names")],
                [
                    InlineKeyboardButton("• sᴇᴛᴛɪɴɢs •", callback_data="settings_info"),
                    InlineKeyboardButton("ᴅᴏɴᴀᴛᴇ •", callback_data="donate")
                ],
                [InlineKeyboardButton("• ʜᴏᴍᴇ", callback_data="home")]
            ])
        )


    elif data == "settings_info":

        await query.message.edit_text(
            Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="help")]
            ])
        )


    elif data == "file_names":

        format_template = await codeflixbots.get_format_template(user_id)

        await query.message.edit_text(
            Txt.FILE_NAME_TXT.format(format_template=format_template),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="help")]
            ])
        )


    elif data == "settings_info":

        await query.message.edit_text(
            Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="help")]
            ])
        )


    elif data == "donate":

        await query.message.edit_text(
            Txt.DONATE_TXT,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="help"),
                    InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/sewxiy")
                ]
            ])
        )


    elif data == "about":

        await query.message.edit_text(
            Txt.ABOUT_TXT,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("• sᴜᴘᴘᴏʀᴛ", url="https://t.me/CodeflixSupport"),
                    InlineKeyboardButton("ᴄᴏᴍᴍᴀɴᴅs •", callback_data="help")
                ],
                [
                    InlineKeyboardButton("• ᴅᴇᴠᴇʟᴏᴘᴇʀ", url="https://t.me/cosmic_freak"),
                    InlineKeyboardButton("ɴᴇᴛᴡᴏʀᴋ •", url="https://t.me/otakuflix_network")
                ],
                [InlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data="home")]
            ])
        )


    elif data == "source":

        await query.message.edit_text(
            Txt.SOURCE_TXT,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ʜᴏᴍᴇ •", callback_data="home")]
            ])
        )


    elif data == "close":

        try:
            await query.message.delete()
        except:
            pass


# ================= HELP COMMAND =================

@Client.on_message(filters.command("help"))
async def help_command(client, message):

    bot = await client.get_me()

    await message.reply_text(
        Txt.HELP_TXT.format(bot.mention),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• ᴀᴜᴛᴏ ʀᴇɴᴀᴍᴇ ғᴏʀᴍᴀᴛ •", callback_data="file_names")],
            [
                InlineKeyboardButton("• sᴇᴛᴛɪɴɢs •", callback_data="settings_info"),
                InlineKeyboardButton("ᴅᴏɴᴀᴛᴇ •", callback_data="donate")
            ],
            [InlineKeyboardButton("• ʜᴏᴍᴇ", callback_data="home")]
        ])
    )
