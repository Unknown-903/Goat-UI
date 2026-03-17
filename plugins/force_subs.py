import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChannelInvalid, PeerIdInvalid
from config import Config

FORCE_SUB_CHANNELS = Config.FORCE_SUB_CHANNELS
IMAGE_URL = "https://graph.org/file/a27d85469761da836337c.jpg"

# Cache: user_id -> (timestamp, is_subscribed)
# Har user ka result 5 min cache karo — repeated API calls avoid karo
_sub_cache = {}
CACHE_TTL = 300  # 5 minutes

async def not_subscribed(_, __, message):
    if not message.from_user:
        return False

    user_id = message.from_user.id

    # Cache check — avoid repeated API calls
    cached = _sub_cache.get(user_id)
    if cached:
        ts, result = cached
        if time.time() - ts < CACHE_TTL:
            return result

    # Check all channels
    for channel in FORCE_SUB_CHANNELS:
        if not channel or not channel.strip():
            continue
        try:
            member = await message._client.get_chat_member(channel.strip(), user_id)
            if member.status in {"kicked", "left"}:
                _sub_cache[user_id] = (time.time(), True)
                return True
        except UserNotParticipant:
            _sub_cache[user_id] = (time.time(), True)
            return True
        except (ChatAdminRequired, ChannelInvalid, PeerIdInvalid):
            # Bot not admin or invalid channel — disable force sub silently
            _sub_cache[user_id] = (time.time(), False)
            return False
        except Exception:
            _sub_cache[user_id] = (time.time(), False)
            return False

    _sub_cache[user_id] = (time.time(), False)
    return False

@Client.on_message(filters.private & filters.create(not_subscribed))
async def forces_sub(client, message):
    not_joined_channels = []
    for channel in FORCE_SUB_CHANNELS:
        try:
            user = await client.get_chat_member(channel, message.from_user.id)
            if user.status in {"kicked", "left"}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)
        except Exception:
            pass  # Bot not admin — skip

    if not not_joined_channels:
        return

    buttons = [
        [
            InlineKeyboardButton(
                text=f"• ᴊᴏɪɴ {channel.capitalize()} •", url=f"https://t.me/{channel}"
            )
        ]
        for channel in not_joined_channels
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="• ᴊᴏɪɴᴇᴅ •", callback_data="check_subscription"
            )
        ]
    )

    text = "**ʙᴀᴋᴋᴀ!!, ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴛᴏ ᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs, ᴊᴏɪɴ ᴛʜᴇ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ**"
    await message.reply_photo(
        photo=IMAGE_URL,
        caption=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("check_subscription"))
async def check_subscription(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    not_joined_channels = []

    for channel in FORCE_SUB_CHANNELS:
        try:
            user = await client.get_chat_member(channel, user_id)
            if user.status in {"kicked", "left"}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)
        except Exception:
            pass  # Bot not admin — skip

    # Clear cache so next message is checked fresh
    _sub_cache.pop(user_id, None)

    if not not_joined_channels:
        new_text = "**ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs. ᴛʜᴀɴᴋ ʏᴏᴜ! 😊 /start ɴᴏᴡ**"
        if callback_query.message.caption != new_text:
            await callback_query.message.edit_caption(
                caption=new_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("• ɴᴏᴡ ᴄʟɪᴄᴋ ʜᴇʀᴇ •", callback_data='help')]
                ])
            )
    else:
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"• ᴊᴏɪɴ {channel.capitalize()} •",
                    url=f"https://t.me/{channel}",
                )
            ]
            for channel in not_joined_channels
        ]
        buttons.append(
            [
                InlineKeyboardButton(
                    text="• ᴊᴏɪɴᴇᴅ •", callback_data="check_subscription"
                )
            ]
        )

        text = "**ʏᴏᴜ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴛʜᴇ ʀᴇǫᴜɪʀᴇᴅ ᴄʜᴀɴɴᴇʟs. ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴛʜᴇ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟs ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ**"
        if callback_query.message.caption != text:
            await callback_query.message.edit_caption(
                caption=text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
