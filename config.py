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

    START_TXT = """
╔═══════════════════════════╗
║   ⚡  G O A T  U I  ⚡   ║
╚═══════════════════════════╝

<b>Hey {}! 👋

I am an Advanced Media Processing Bot.
━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬  Encode    •    🗜️  Compress
🔀  Merge     •    🔍  Upscale
✏️  Rename    •    ⚙️  Settings

Use /help to see all commands.</b>
"""

    HELP_TXT = """
╔═══════════════════════════╗
║    📋  C O M M A N D S    ║
╚═══════════════════════════╝

<b>🎬  ENCODE
</b><code>/encode</code> — Reply to a video to encode it

<b>🗜️  COMPRESS
</b><code>/compress</code> — Reply to a video to compress it

<b>🔀  MERGE
</b><code>/merge</code> — Start a merge session
<code>/done</code> — Finish and merge all files
<code>/mergecancel</code> — Cancel active session

<b>🔍  UPSCALE
</b><code>/upscale</code> — Reply to an image to upscale it

<b>✏️  RENAME
</b><code>/autorename</code> — Set auto rename format
<code>/select 1-12</code> — Set episode range

<b>⚙️  SETTINGS
</b><code>/settings</code> — Manage thumbnail and metadata

<b>📊  STATUS
</b><code>/status</code> — View all active tasks

"""

    FILE_NAME_TXT = """
╔═══════════════════════════╗
║  ✏️  A U T O  R E N A M E  ║
╚═══════════════════════════╝

<b>Set your rename format:
<code>/autorename Anime S{season}E{episode} {quality}</code>

Placeholders:
• <code>{season}</code>   — Season number
• <code>{episode}</code>  — Episode number
• <code>{quality}</code>  — Quality (1080p etc)

Current Format:
{format_template}</b>
"""

    PROGRESS_BAR = """
<b>» Size</b>  : {1} | {2}
<b>» Done</b>  : {0}%
<b>» Speed</b> : {3}/s
<b>» ETA</b>   : {4}
"""

    SEND_METADATA = """
╔═══════════════════════════╗
║  🏷️  M E T A D A T A      ║
╚═══════════════════════════╝

<b>Use /settings → 🏷️ Metadata
to set Title, Author and Artist tags.</b>
"""

    THUMBNAIL_TXT = """
╔═══════════════════════════╗
║  🖼️  T H U M B N A I L    ║
╚═══════════════════════════╝

<b>Use /settings → 🖼️ Thumbnail
to upload and manage your thumbnail.</b>
"""

    DONATE_TXT = """
╔═══════════════════════════╗
║    💝  S U P P O R T      ║
╚═══════════════════════════╝

<b>Enjoying the bot? Consider supporting! ❤️

Every contribution keeps the bot running. 🚀</b>
"""

    SOURCE_TXT = """
╔═══════════════════════════╗
║    📦  S O U R C E        ║
╚═══════════════════════════╝

<b>This bot is a private project.

For support or queries, contact the owner.</b>
"""

    ABOUT_TXT = """
╔═══════════════════════════╗
║    ℹ️  A B O U T  B O T   ║
╚═══════════════════════════╝

<b>⚡ Goat UI — Advanced Media Bot

🎯 Features:
• 🎬 H.265 Video Encoding
• 🗜️ Smart Compression
• 🔀 Multi-file Merging
• 🔍 AI Image Upscaling
• ✏️ Auto File Renaming
• ⚙️ Custom Metadata and Thumbnail
• 📊 Live Task Status

👨‍💻 Developer : @cosmic_freak
📢 Updates   : @Codeflix_Bots</b>
"""

    CAPTION_TXT = ""
