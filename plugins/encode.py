import os
import time
import asyncio
import logging
from collections import deque

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from helper.utils import progress_for_pyrogram
from helper.auth import auth_chats
from helper.database import codeflixbots
from helper.permissions import is_owner, is_admin as _perm_is_admin, is_authorized_chat
from config import Config

import sys

# Docker mein stdout pe force karo - tabhi logs `docker logs` mein dikhenge
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ================= ADMIN CHECK =================

def _is_admin_encode(user_id):
    return _perm_is_admin(user_id)

# ================= SETTINGS =================

RESOLUTIONS = {
    "480p": "854:480",
    "720p": "1280:720",
    "1080p": "1920:1080",
    "4k": "3840:2160"
}

DEFAULT_CRF = {
    "480p": 28,
    "720p": 26,
    "1080p": 24,
    "4k": 22
}

# Minimum bitrate floor (kbps) — inse niche kabhi nahi jaana
MIN_BITRATE = {
    "480p":  350,
    "720p":  700,
    "1080p": 1400,
    "4k":    3000,
}

# Maximum bitrate ceiling (kbps) — inse upar kabhi nahi jaana
MAX_BITRATE = {
    "480p":  1200,
    "720p":  2500,
    "1080p": 4500,
    "4k":    9000,
}

# Base size per minute (MB/min) — duration ke saath scale hoga
SIZE_PER_MIN = {
    "480p":  2.5,   # ~50MB for 20min, ~120MB for 48min
    "720p":  5.0,   # ~100MB for 20min, ~240MB for 48min
    "1080p": 8.5,   # ~170MB for 20min, ~408MB for 48min
    "4k":    20.0,
}

PRESETS = [
    "ultrafast",
    "superfast",
    "veryfast",
    "fast",
    "medium",
    "slow"
]

# Compress level: CRF values
COMPRESS_LEVELS = {
    "low":    {"crf_add": 2,  "label": "🟢 Low"},
    "medium": {"crf_add": 5,  "label": "🟡 Medium"},
    "high":   {"crf_add": 8,  "label": "🟠 High"},
    "best":   {"crf_add": 12, "label": "🔴 Best"},
}


def get_video_duration(file_path):
    """ffprobe se video duration seconds mein nikalo"""
    import subprocess
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except:
        return None


def calc_video_bitrate(duration_sec, quality, audio_bitrate_kbps=128):
    """Duration ke hisaab se adaptive bitrate — chhoti file chhoti, badi file badi"""
    minutes = duration_sec / 60
    target_mb = SIZE_PER_MIN.get(quality, 5.0) * minutes
    target_bits = target_mb * 8 * 1024 * 1024
    total_kbps = (target_bits / duration_sec) / 1000
    video_kbps = int(total_kbps - audio_bitrate_kbps)
    # Floor aur ceiling dono enforce karo
    video_kbps = max(video_kbps, MIN_BITRATE.get(quality, 350))
    video_kbps = min(video_kbps, MAX_BITRATE.get(quality, 2500))
    return video_kbps


def calc_max_bitrate(duration_sec, quality, audio_bitrate_kbps=128):
    """maxrate hamesha target se 40% zyada — kabhi target se kam nahi"""
    target = calc_video_bitrate(duration_sec, quality, audio_bitrate_kbps)
    return min(int(target * 1.4), int(MAX_BITRATE.get(quality, 2500) * 1.2))

# Patience messages — time lag raha ho toh dikhao
PATIENCE_MSGS = [
    "☕ Chai pi lo, thoda time lagega...",
    "🍿 Popcorn ready karo, abhi aa raha hai!",
    "😴 Thoda so jao, hum kaam kar rahe hain...",
    "🐢 H.265 encoding slow hoti hai, quality ke liye worth it hai!",
    "🔧 FFmpeg mehnat kar raha hai aapke liye...",
    "🎬 Hollywood movie bhi itni mehnat se banti hai!",
    "⚡ Server full speed pe hai, bas thoda sabr karo...",
    "🧘 Patience is a virtue... aur encoding bhi!",
    "🚀 Quality encode ho rahi hai, rush mat karo!",
    "💪 Jitna bada file, utna zyada time — normal hai!",
]

# ================= QUEUE =================

encode_queue = asyncio.Queue()
queue_list = deque()
active_tasks = {}
workers_started = False

rename_wait = {}
cancel_tasks = {}

# ================= WORKER =================

async def start_workers(client):
    global workers_started
    if workers_started:
        return
    workers_started = True
    asyncio.create_task(worker(client))


async def worker(client):
    while True:
        task = await encode_queue.get()
        active_tasks[task["id"]] = task
        try:
            await start_encode(client, task)
        except Exception as e:
            logger.error(e)
        active_tasks.pop(task["id"], None)
        try:
            queue_list.remove(task)
        except:
            pass
        encode_queue.task_done()


# ================= ENCODE COMMAND =================

@Client.on_message((filters.private | filters.group) & filters.command("encode") & filters.reply)
async def encode_cmd(client, message):
    user_id = message.from_user.id
    if not _is_admin_encode(user_id):
        return await message.reply_text("❌ Sirf owner/admin use kar sakta hai.")
    if message.chat.type in ["group", "supergroup"]:
        if not is_authorized_chat(message.chat.id):
            return await message.reply_text("❌ Yeh group authorized nahi hai.")
    if not message.reply_to_message:
        await message.reply_text("❌ Reply to a video or file")
        return
    if not (message.reply_to_message.video or message.reply_to_message.document):
        await message.reply_text("❌ Reply to a downloadable media file")
        return

    rename_wait[user_id] = {
        "msg": message.reply_to_message
    }

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎬 480p", callback_data="quality|480p"),
            InlineKeyboardButton("📺 720p", callback_data="quality|720p")
        ],
        [
            InlineKeyboardButton("🔥 1080p", callback_data="quality|1080p"),
            InlineKeyboardButton("💎 4K", callback_data="quality|4k")
        ]
    ])

    await message.reply_text(
        "<b>Select Encode Quality</b>",
        reply_markup=buttons
    )
    await start_workers(client)


# ================= QUALITY SELECT =================

@Client.on_callback_query(filters.regex("^quality"))
async def quality_select(client, query):
    _, quality = query.data.split("|")
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Rename", callback_data=f"rename_yes|{quality}"),
            InlineKeyboardButton("No Rename", callback_data=f"rename_no|{quality}")
        ]
    ])
    await query.message.edit_text("Rename file?", reply_markup=buttons)


# ================= RENAME YES =================

@Client.on_callback_query(filters.regex("^rename_yes"))
async def rename_yes(client, query):
    _, quality = query.data.split("|")
    user_id = query.from_user.id
    data = rename_wait.get(user_id)

    if not data or "msg" not in data:
        await query.answer("Session expired. Please send /encode again.", show_alert=True)
        return

    rename_wait[user_id] = {
        "quality": quality,
        "msg": data["msg"],
        "waiting_rename": True
    }
    await query.message.edit_text("Send new file name\nExample: Episode 10")

# ================= GET RENAME =================

@Client.on_message(
    (filters.private | filters.group) &
    filters.text &
    ~filters.command(["encode","tasks","start","help","setthumb","delthumb","viewthumb",
                      "setcaption","delcaption","seecaption","metadata","delmetadata",
                      "addadmin","removeadmin","adminlist","authgroup","unauthgroup",
                      "authlist","rename","queue","logs","batch","cancelbatch"]),
    group=1
)
async def get_rename(client, message):
    user_id = message.from_user.id
    if user_id not in rename_wait:
        return

    data = rename_wait.get(user_id)
    if not data or not data.get("waiting_rename"):
        return

    rename_wait.pop(user_id)
    quality = data.get("quality")
    msg = data.get("msg")
    rename = message.text

    if not quality or not msg:
        await message.reply_text("❌ Session expired. Please send /encode again.")
        return

    task = {
        "id": int(time.time()*1000),
        "user": user_id,
        "quality": quality,
        "rename": rename,
        "crf": DEFAULT_CRF[quality],
        "msg": msg,
        "name": message.from_user.first_name
    }

    queue_list.append(task)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡ ultrafast", callback_data=f"preset|{task['id']}|ultrafast"),
            InlineKeyboardButton("🚀 superfast", callback_data=f"preset|{task['id']}|superfast")
        ],
        [
            InlineKeyboardButton("🔥 veryfast", callback_data=f"preset|{task['id']}|veryfast"),
            InlineKeyboardButton("⚙️ fast", callback_data=f"preset|{task['id']}|fast")
        ]
    ])

    await message.reply_text(
        "⚡ Select Encoding Speed\n\n"
        "⚡ ultrafast — sabse fast, ~10-15 min\n"
        "🚀 superfast — fast, ~15-20 min\n"
        "🔥 veryfast — balanced, ~20-30 min\n"
        "⚙️ fast — better quality, ~35-45 min",
        reply_markup=buttons
    )

# ================= RENAME NO =================

@Client.on_callback_query(filters.regex("^rename_no"))
async def rename_no(client, query):
    _, quality = query.data.split("|")
    user_id = query.from_user.id
    msg = rename_wait.get(user_id, {}).get("msg")

    if not msg:
        await query.answer("Media not found", show_alert=True)
        return

    task = {
        "id": int(time.time()*1000),
        "user": user_id,
        "quality": quality,
        "rename": None,
        "crf": DEFAULT_CRF[quality],
        "msg": msg,
        "name": query.from_user.first_name
    }

    queue_list.append(task)
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚡ ultrafast", callback_data=f"preset|{task['id']}|ultrafast"),
            InlineKeyboardButton("🚀 superfast", callback_data=f"preset|{task['id']}|superfast")
        ],
        [
            InlineKeyboardButton("🔥 veryfast", callback_data=f"preset|{task['id']}|veryfast"),
            InlineKeyboardButton("⚙️ fast", callback_data=f"preset|{task['id']}|fast")
        ]
    ])
    await query.message.edit_text(
        "⚡ Select Encoding Speed\n\n"
        "⚡ ultrafast — sabse fast, ~10-15 min\n"
        "🚀 superfast — fast, ~15-20 min\n"
        "🔥 veryfast — balanced, ~20-30 min\n"
        "⚙️ fast — better quality, ~35-45 min",
        reply_markup=buttons
    )


# ================= PRESET SELECT =================

@Client.on_callback_query(filters.regex("^preset"))
async def preset_select(client, query):
    _, task_id, preset = query.data.split("|")
    task_id = int(task_id)

    for task in queue_list:
        if task["id"] == task_id:
            task["preset"] = preset
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🟢 Low", callback_data=f"compress|{task_id}|low"),
                    InlineKeyboardButton("🟡 Medium", callback_data=f"compress|{task_id}|medium")
                ],
                [
                    InlineKeyboardButton("🟠 High", callback_data=f"compress|{task_id}|high"),
                    InlineKeyboardButton("🔴 Best", callback_data=f"compress|{task_id}|best")
                ],
                [
                    InlineKeyboardButton("⏭️ Skip Compress", callback_data=f"compress|{task_id}|skip")
                ]
            ])
            await query.message.edit_text(
                "🗜️ Select Compression Level\n\n"
                "🟢 Low — ~10% smaller, best quality\n"
                "🟡 Medium — ~30% smaller, good quality\n"
                "🟠 High — ~50% smaller, decent quality\n"
                "🔴 Best — ~70% smaller, max compression\n"
                "⏭️ Skip — no compression",
                reply_markup=buttons
            )
            return


# ================= COMPRESS SELECT =================

@Client.on_callback_query(filters.regex("^compress"))
async def compress_select(client, query):
    _, task_id, level = query.data.split("|")
    task_id = int(task_id)
    user_id = query.from_user.id

    for task in queue_list:
        if task["id"] == task_id:
            if task["user"] != user_id:
                await query.answer("❌ Ye tumhara task nahi hai!", show_alert=True)
                return
            task["compress_level"] = level
            await encode_queue.put(task)
            label = "Skip" if level == "skip" else level.capitalize()
            compress_note = "" if level == "skip" else f" (encode+compress merged ✅)"
            await query.message.edit_text(
                f"📥 Added to Encode Queue\n\n🎬 {task['quality']} | ⚡ {task['preset']} | 🗜️ {label}{compress_note}"
            )
            return


# ================= TASKS COMMAND =================

@Client.on_message(filters.command("tasks") & (filters.private | filters.group))
async def tasks_cmd(client, message):
    user_id = message.from_user.id
    if not _is_admin_encode(user_id):
        return

    if not queue_list and not active_tasks:
        await message.reply_text("📭 Queue khali hai, koi task nahi chal raha.")
        return

    text = "📋 **Encode Queue Status**\n\n"

    if active_tasks:
        text += f"🔄 **Chal raha hai ({len(active_tasks)}):**\n"
        for tid, task in active_tasks.items():
            compress = task.get("compress_level", "skip")
            text += f"  ▶️ `{task['name']}` — {task['quality']} | {task.get('preset', '?')} | 🗜️ {compress}\n"
        text += "\n"

    waiting = [t for t in queue_list if t['id'] not in active_tasks]
    if waiting:
        text += f"⏳ **Wait mein ({len(waiting)}):**\n"
        for i, task in enumerate(waiting, 1):
            compress = task.get("compress_level", "?")
            text += f"  {i}. `{task['name']}` — {task['quality']} | {task.get('preset', '?')} | 🗜️ {compress}\n"

    await message.reply_text(text)


# ================= CANCEL =================

@Client.on_callback_query(filters.regex("^cancel"))
async def cancel_task_encode(client, query):
    parts = query.data.split("|")
    if len(parts) != 3:
        return await query.answer("Invalid cancel data", show_alert=True)

    _, task_id, owner_id = parts
    task_id = int(task_id)
    owner_id = int(owner_id)
    caller_id = query.from_user.id

    # Task owner — apna cancel kar sakta hai
    if caller_id == owner_id:
        pass
    # Bot owner — kisi ka bhi cancel kar sakta hai
    elif caller_id == Config.OWNER_ID:
        pass
    # Admin — sirf apna cancel kar sakta hai, dusre admin ka nahi
    else:
        return await query.answer("❌ Ye tumhara task nahi hai!", show_alert=True)

    cancel_tasks[task_id] = True
    await query.answer("✅ Cancel request bheja gaya")


# ================= ENCODING =================

async def start_encode(client, task):

    msg = task["msg"]
    user_id = task["user"]
    quality = task["quality"]
    preset = task.get("preset", "veryfast")
    rename = task["rename"]
    crf = task["crf"]

    scale = RESOLUTIONS[quality]

    download = f"temp_{task['id']}.mkv"
    encoded = f"enc_{task['id']}.mkv"

    cancel_tasks[task['id']] = False

    # ---------------- DOWNLOAD ----------------

    progress_msg = await msg.reply_text(
        "📥 Downloading...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel|{task['id']}|{user_id}")]]
        )
    )

    start_time = time.time()

    logger.info(f"[{task['id']}] Download started for user {user_id}")
    file_path = await client.download_media(
        msg,
        file_name=download,
        progress=progress_for_pyrogram,
        progress_args=("📥 Downloading...", progress_msg, start_time, f"cancel|{task['id']}|{user_id}")
    )

    logger.info(f"[{task['id']}] Download complete: {file_path}")

    if cancel_tasks.get(task['id']):
        await progress_msg.edit("❌ Download Cancelled")
        return

    # ---------------- ENCODE ----------------

    await progress_msg.edit(
        "⚙️ Encoding...\n\n⬡⬡⬡⬡⬡⬡⬡⬡⬡⬡ 0%",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel|{task['id']}|{user_id}")]]
        )
    )

    # Duration nikalo for bitrate calculation
    duration = get_video_duration(file_path)

    # Compress level — agar select hai toh encode bitrate hi adjust karo, alag pass nahi
    compress_level = task.get("compress_level", "skip")
    compress_ratio = {
        "low":    0.85,
        "medium": 0.65,
        "high":   0.45,
        "best":   0.30,
        "skip":   1.0,
    }
    ratio = compress_ratio.get(compress_level, 1.0)

    if duration and duration > 0:
        video_bitrate = int(calc_video_bitrate(duration, quality) * ratio)
        max_bitrate = int(calc_max_bitrate(duration, quality) * ratio)
        # Floor enforce karo
        min_floor = MIN_BITRATE.get(quality, 350)
        video_bitrate = max(video_bitrate, min_floor)
        max_bitrate = max(max_bitrate, int(video_bitrate * 1.4))
        logger.info(f"[{task['id']}] Duration={duration:.1f}s | bitrate={video_bitrate}k | max={max_bitrate}k | compress={compress_level}")
        use_bitrate = True
    else:
        logger.warning(f"[{task['id']}] Duration detect nahi hui, CRF fallback")
        use_bitrate = False

    fast_presets = {"ultrafast", "superfast", "veryfast"}
    if preset in fast_presets:
        x265_params = "log-level=error:aq-mode=0:no-sao=1:no-deblock=1"
    else:
        x265_params = "log-level=error:aq-mode=1:me=hex:subme=1:ref=1"

    threads = "4"

    if use_bitrate:
        cmd = [
            "ffmpeg",
            "-progress", "pipe:1",
            "-stats_period", "3",
            "-nostats",
            "-threads", threads,
            "-i", file_path,
            "-map", "0",
            "-vf", f"scale={scale}:flags=bilinear",
            "-c:v", "libx265",
            "-preset", preset,
            "-b:v", f"{video_bitrate}k",
            "-maxrate", f"{max_bitrate}k",
            "-bufsize", f"{max_bitrate * 2}k",
            "-x265-params", x265_params,
            "-c:a", "aac",
            "-b:a", "128k",
            "-c:s", "copy",
            "-tag:v", "hvc1",
            "-y",
            encoded
        ]
    else:
        cmd = [
            "ffmpeg",
            "-progress", "pipe:1",
            "-stats_period", "3",
            "-nostats",
            "-threads", threads,
            "-i", file_path,
            "-map", "0",
            "-vf", f"scale={scale}:flags=bilinear",
            "-c:v", "libx265",
            "-preset", preset,
            "-crf", str(crf),
            "-x265-params", x265_params,
            "-c:a", "aac",
            "-b:a", "128k",
            "-c:s", "copy",
            "-tag:v", "hvc1",
            "-y",
            encoded
        ]

    logger.info(f"[{task['id']}] Encode started | quality={quality} preset={preset} crf={crf}")
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # stderr ko background mein drain karo — warna buffer full hoke hang hoga
    async def drain_stderr(proc):
        try:
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
        except:
            pass

    asyncio.create_task(drain_stderr(process))

    last_edit_time = 0
    encode_start = time.time()
    patience_index = 0
    duration_us = int(duration * 1_000_000) if duration else 0
    progress = 0
    _enc_editing = False

    async def safe_enc_edit(text):
        nonlocal _enc_editing, last_edit_time
        if _enc_editing:
            return
        _enc_editing = True
        try:
            await progress_msg.edit(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel|{task['id']}|{user_id}")]]
                )
            )
            last_edit_time = time.time()
        except FloodWait as e:
            last_edit_time = time.time() + e.value
        except:
            pass
        finally:
            _enc_editing = False

    logger.info(f"[{task['id']}] Reading stdout progress... duration_us={duration_us}")

    while True:

        if cancel_tasks.get(task['id']):
            process.kill()
            await progress_msg.edit("❌ Encode Cancelled")
            return

        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout=60)
        except asyncio.TimeoutError:
            logger.warning(f"[{task['id']}] Stdout readline timeout — breaking")
            break

        if not line:
            break

        text = line.decode("utf-8").strip()

        if text.startswith("out_time_us="):
            try:
                out_us = int(text.split("=")[1])
                if duration_us > 0:
                    progress = min(int(out_us * 100 / duration_us), 99)
                else:
                    progress = 0
            except:
                pass

            now = time.time()
            elapsed = int(now - encode_start)

            if now - last_edit_time >= 10:
                last_edit_time = now  # turant update — multiple tasks na ban
                filled = "⬢" * (progress // 10)
                empty = "⬡" * (10 - progress // 10)

                if elapsed > 45:
                    patience = PATIENCE_MSGS[patience_index % len(PATIENCE_MSGS)]
                    patience_index += 1
                    status_text = f"⚙️ Encoding...\n\n{filled}{empty} {progress}%\n\n{patience}"
                else:
                    status_text = f"⚙️ Encoding...\n\n{filled}{empty} {progress}%"

                asyncio.create_task(safe_enc_edit(status_text))

    # stderr already drained via drain_stderr task
    # wait_for prevents indefinite hang
    try:
        await asyncio.wait_for(process.wait(), timeout=120)
    except asyncio.TimeoutError:
        logger.warning(f"[{task['id']}] Encode wait timeout, killing")
        process.kill()
    logger.info(f"[{task['id']}] Encode complete")

    try:
        await progress_msg.edit("⚙️ Encoding...\n\n⬢⬢⬢⬢⬢⬢⬢⬢⬢⬢ 100% ✅")
    except:
        pass

    # ---------------- RENAME ----------------
    if rename:
        name = f"{rename}.mkv"
    else:
        if msg.document and msg.document.file_name:
            name = msg.document.file_name
        elif msg.video and msg.video.file_name:
            name = msg.video.file_name
        else:
            name = f"encoded_{task['id']}.mkv"

    name = os.path.splitext(name)[0] + ".mkv"

    # ---------------- METADATA (encode ke saath hi) ----------------
    title = await codeflixbots.get_title(user_id) or ""
    author = await codeflixbots.get_author(user_id) or ""
    artist = await codeflixbots.get_artist(user_id) or ""

    meta_file = f"meta_{task['id']}.mkv"

    logger.info(f"[{task['id']}] Adding metadata via remux (fast copy)")
    await progress_msg.edit("🏷️ Applying Metadata...")

    meta_cmd = [
        "ffmpeg",
        "-i", encoded,
        "-map", "0",
        "-c", "copy",
        "-metadata", f"title={title}",
        "-metadata", f"author={author}",
        "-metadata", f"artist={artist}",
        "-y",
        meta_file
    ]

    meta_process = await asyncio.create_subprocess_exec(
        *meta_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    try:
        await asyncio.wait_for(meta_process.wait(), timeout=120)
    except asyncio.TimeoutError:
        meta_process.kill()

    # metadata success hogi toh meta_file use karo, warna encoded directly
    if os.path.exists(meta_file) and os.path.getsize(meta_file) > 0:
        os.remove(encoded)
        os.rename(meta_file, name)
    else:
        os.rename(encoded, name)

    # ---------------- THUMB ----------------
    thumb = None
    thumb_id = await codeflixbots.get_thumbnail(user_id)

    if thumb_id:
        try:
            thumb = await client.download_media(
                thumb_id,
                file_name=f"thumb_{task['id']}.jpg"
            )
        except:
            thumb = None

    logger.info(f"[{task['id']}] Upload started")
    # ---------------- UPLOAD ----------------
    await progress_msg.edit(
        "📤 Uploading...",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Cancel", callback_data=f"cancel|{task['id']}|{user_id}")]]
        )
    )

    while True:

        if cancel_tasks.get(task['id']):
            await progress_msg.edit("❌ Upload Cancelled")
            return

        try:

            start_time = time.time()

            await client.send_document(
                chat_id=user_id,
                document=name,
                caption=name,
                thumb=thumb if thumb else None,
                progress=progress_for_pyrogram,
                progress_args=("📤 Uploading...", progress_msg, start_time, f"cancel|{task['id']}|{user_id}")
            )

            break

        except FloodWait as e:
            await asyncio.sleep(e.value)

    logger.info(f"[{task['id']}] Task complete, cleaning up")
    # ---------------- CLEANUP ----------------
    await progress_msg.delete()
    for f in [file_path, name, thumb]:
        try:
            if f and os.path.exists(f):
                os.remove(f)
        except:
            pass
