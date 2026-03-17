import re
import os
import time

id_pattern = re.compile(r'^.\d+$')


class Config(object):

    # ================= BOT CONFIG =================
    API_ID    = int(os.environ.get("API_ID", 29776284))
    API_HASH  = os.environ.get("API_HASH", "aa9d8ca9cf83f30aa897effa6296493a")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8142527078:AAFifGQPKZPIz2ZnGXIGOGYFlZdheNrmxec")

    # ================= OWNER =================
    OWNER_ID = int(os.environ.get("OWNER_ID", "7224871892"))

    # ================= DATABASE =================
    DB_NAME = os.environ.get("DB_NAME", "Yato")
    DB_URL  = os.environ.get(
        "DB_URL",
        "mongodb+srv://Toonpro12:animebash@cluster0.e6hpn8l.mongodb.net/?retryWrites=true&w=majority"
    )

    PORT       = int(os.environ.get("PORT", "8080"))
    BOT_UPTIME = time.time()
    WEBHOOK    = os.environ.get("WEBHOOK", "True").lower() == "true"

    START_PIC = os.environ.get(
        "START_PIC",
        "https://graph.org/file/29a3acbbab9de5f45a5fe.jpg"
    )

    # ================= ADMINS =================
    ADMIN = [
        int(admin) if id_pattern.search(admin) else admin
        for admin in os.environ.get("ADMIN", "1889175355 7224871892").split()
    ]

    # ================= CHANNELS =================
    FORCE_SUB_CHANNELS = os.environ.get(
        "FORCE_SUB_CHANNELS", "sharktoonsindia"
    ).split(",")

    LOG_CHANNEL  = int(os.environ.get("LOG_CHANNEL",  "-1002913785995"))
    DUMP_CHANNEL = int(os.environ.get("DUMP_CHANNEL", "-1002913785995"))


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
