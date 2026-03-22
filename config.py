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
        "https://i.ibb.co/jZDxWgmk/dbffcd55fcb3.jpg"
    )

    # ================= ADMINS =================
    ADMIN = [
        int(admin) if id_pattern.search(admin) else admin
        for admin in os.environ.get("ADMIN", "1889175355 7224871892").split()
    ]

    # ================= CHANNELS =================
    LOG_CHANNEL  = int(os.environ.get("LOG_CHANNEL",  "-1002913785995"))
    DUMP_CHANNEL = int(os.environ.get("DUMP_CHANNEL", "-1002913785995"))
