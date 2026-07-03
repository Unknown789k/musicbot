"""
✧･ﾟ: *✧･ﾟ:*  VΛПIΧ MЦSIC BӨƬ  *:･ﾟ✧*:･ﾟ✧
         ⋆⋅☆⋅⋆  Premium Edition (Admin Tools + Promote)  ⋆⋅☆⋅⋆
"""

import asyncio
import os
import json
from typing import Dict, List
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ChatPermissions
)
from pyrogram.enums import ChatMemberStatus
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped, VideoStream
from pytgcalls.exceptions import NoActiveGroupCall
import yt_dlp

# ============================================================
# ⚙️ CONFIGURATION - Environment Variables से लें (Railway/Server)
# ============================================================

API_ID = int(os.environ.get("API_ID", 12345))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
SESSION_STRING = os.environ.get("SESSION_STRING", "your_session_string")

BOT_NAME = "VΛПIΧ MЦSIC BӨƬ"
BOT_USERNAME = "@vanixmusic_bot"

# ============================================================
# 🗄️ DATABASE SETUP (JSON)
# ============================================================

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"warnings": {}, "welcome": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_data()
warnings = db.get("warnings", {})
welcome_msgs = db.get("welcome", {})

def update_db():
    db["warnings"] = warnings
    db["welcome"] = welcome_msgs
    save_data(db)

# ============================================================
# 🚀 BOT INITIALIZATION
# ============================================================

app = Client(
    name="vanixmusic",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    session_string=SESSION_STRING,
)

call = PyTgCalls(app)

# ============================================================
# 📊 GLOBAL STATE (Music)
# ============================================================

queues: Dict[int, List[dict]] = {}
current_track: Dict[int, dict] = {}
loop_status: Dict[int, bool] = {}
playing_status: Dict[int, bool] = {}

# ============================================================
# 🎵 YT-DLP HELPERS
# ============================================================

async def get_audio_info(query: str) -> dict:
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
    }
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            duration = info.get('duration', 0)
            if duration:
                mins, secs = divmod(duration, 60)
                duration_str = f"{mins:02d}:{secs:02d}"
            else:
                duration_str = "🔴 Live"
            return {
                'title': info.get('title', 'Unknown'),
                'duration': duration,
                'duration_str': duration_str,
                'url': info['url'],
                'webpage_url': info.get('webpage_url', ''),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
    return await loop.run_in_executor(None, extract)

async def get_video_info(query: str) -> dict:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
    }
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            duration = info.get('duration', 0)
            if duration:
                mins, secs = divmod(duration, 60)
                duration_str = f"{mins:02d}:{secs:02d}"
            else:
                duration_str = "🔴 Live"
            return {
                'title': info.get('title', 'Unknown'),
                'duration': duration,
                'duration_str': duration_str,
                'url': info['url'],
                'webpage_url': info.get('webpage_url', ''),
                'thumbnail': info.get('thumbnail', ''),
            }
    return await loop.run_in_executor(None, extract)

# ============================================================
# 🎶 MUSIC PLAYBACK ENGINE
# ============================================================

async def play_next(chat_id: int):
    if loop_status.get(chat_id, False) and chat_id in current_track:
        queues[chat_id].insert(0, current_track[chat_id])
    if not queues.get(chat_id):
        try:
            await call.leave_call(chat_id)
        except Exception:
            pass
        current_track[chat_id] = {}
        playing_status[chat_id] = False
        return
    song = queues[chat_id].pop(0)
    current_track[chat_id] = song
    playing_status[chat_id] = True
    try:
        await call.join_call(chat_id)
        await call.play(chat_id, AudioPiped(song['url']))
        await send_now_playing(chat_id, song)
    except Exception as e:
        await app.send_message(chat_id, f"❌ <b>Error:</b> <code>{str(e)}</code>", parse_mode="html")
        await play_next(chat_id)

async def send_now_playing"""
✧･ﾟ: *✧･ﾟ:*  VΛПIΧ MЦSIC BӨƬ  *:･ﾟ✧*:･ﾟ✧
         ⋆⋅☆⋅⋆  Premium Edition (Admin Tools + Promote)  ⋆⋅☆⋅⋆
"""

import asyncio
import os
import json
from typing import Dict, List
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ChatPermissions
)
from pyrogram.enums import ChatMemberStatus
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped, VideoStream
from pytgcalls.exceptions import NoActiveGroupCall
import yt_dlp

# ============================================================
# ⚙️ CONFIGURATION - Environment Variables से लें (Railway/Server)
# ============================================================

API_ID = int(os.environ.get("API_ID", 12345))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
SESSION_STRING = os.environ.get("SESSION_STRING", "your_session_string")

BOT_NAME = "VΛПIΧ MЦSIC BӨƬ"
BOT_USERNAME = "@vanixmusic_bot"

# ============================================================
# 🗄️ DATABASE SETUP (JSON)
# ============================================================

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"warnings": {}, "welcome": {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

db = load_data()
warnings = db.get("warnings", {})
welcome_msgs = db.get("welcome", {})

def update_db():
    db["warnings"] = warnings
    db["welcome"] = welcome_msgs
    save_data(db)

# ============================================================
# 🚀 BOT INITIALIZATION
# ============================================================

app = Client(
    name="vanixmusic",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    session_string=SESSION_STRING,
)

call = PyTgCalls(app)

# ============================================================
# 📊 GLOBAL STATE (Music)
# ============================================================

queues: Dict[int, List[dict]] = {}
current_track: Dict[int, dict] = {}
loop_status: Dict[int, bool] = {}
playing_status: Dict[int, bool] = {}

# ============================================================
# 🎵 YT-DLP HELPERS
# ============================================================

async def get_audio_info(query: str) -> dict:
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
    }
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            duration = info.get('duration', 0)
            if duration:
                mins, secs = divmod(duration, 60)
                duration_str = f"{mins:02d}:{secs:02d}"
            else:
                duration_str = "🔴 Live"
            return {
                'title': info.get('title', 'Unknown'),
                'duration': duration,
                'duration_str': duration_str,
                'url': info['url'],
                'webpage_url': info.get('webpage_url', ''),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
    return await loop.run_in_executor(None, extract)

async def get_video_info(query: str) -> dict:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'extract_flat': False,
    }
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            duration = info.get('duration', 0)
            if duration:
                mins, secs = divmod(duration, 60)
                duration_str = f"{mins:02d}:{secs:02d}"
            else:
                duration_str = "🔴 Live"
            return {
                'title': info.get('title', 'Unknown'),
                'duration': duration,
                'duration_str': duration_str,
                'url': info['url'],
                'webpage_url': info.get('webpage_url', ''),
                'thumbnail': info.get('thumbnail', ''),
            }
    return await loop.run_in_executor(None, extract)

# ============================================================
# 🎶 MUSIC PLAYBACK ENGINE
# ============================================================

async def play_next(chat_id: int):
    if loop_status.get(chat_id, False) and chat_id in current_track:
        queues[chat_id].insert(0, current_track[chat_id])
    if not queues.get(chat_id):
        try:
            await call.leave_call(chat_id)
        except Exception:
            pass
        current_track[chat_id] = {}
        playing_status[chat_id] = False
        return
    song = queues[chat_id].pop(0)
    current_track[chat_id] = song
    playing_status[chat_id] = True
    try:
        await call.join_call(chat_id)
        await call.play(chat_id, AudioPiped(song['url']))
        await send_now_playing(chat_id, song)
    except Exception as e:
        await app.send_message(chat_id, f"❌ <b>Error:</b> <code>{str(e)}</code>", parse_mode="html")
        await play_next(chat_id)

async def send_now_playing(chat_id: int, song: dict):
    """Now Playing with Thumbnail + Fancy Formatting"""
    duration = song.get('duration_str', 'Unknown')
    text = (
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n"
        f"<b>   ⋆⋅☆⋅⋆  𝐍𝐎𝐖 𝐏𝐋𝐀𝐘𝐈𝐍𝐆  ⋆⋅☆⋅⋆</b>\n"
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n\n"
        f"<b>🎵 𝐓𝐢𝐭𝐥𝐞:</b> <a href='{song['webpage_url']}'>{song['title']}</a>\n"
        f"<b>⏱ 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧:</b> <code>{duration}</code>\n"
        f"<b>👤 𝐔𝐩𝐥𝐨𝐚𝐝𝐞𝐫:</b> {song.get('uploader', 'Unknown')}\n"
        f"<b>👀 𝐕𝐢𝐞𝐰𝐬:</b> {song.get('view_count', 0):,}\n\n"
        f"<b>📊 𝐐𝐮𝐞𝐮𝐞:</b> <code>{len(queues.get(chat_id, []))}</code> songs remaining"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ 𝐏𝐚𝐮𝐬𝐞", callback_data="pause"),
            InlineKeyboardButton("▶️ 𝐑𝐞𝐬𝐮𝐦𝐞", callback_data="resume"),
        ],
        [
            InlineKeyboardButton("⏭ 𝐒𝐤𝐢𝐩", callback_data="skip"),
            InlineKeyboardButton("🔁 𝐋𝐨𝐨𝐩", callback_data="loop"),
        ],
        [
            InlineKeyboardButton("⏹ 𝐒𝐭𝐨𝐩", callback_data="stop"),
            InlineKeyboardButton("📋 𝐐𝐮𝐞𝐮𝐞", callback_data="queue"),
        ]
    ])
    if song.get('thumbnail'):
        try:
            await app.send_photo(chat_id, photo=song['thumbnail'], caption=text, reply_markup=keyboard, parse_mode="html")
        except Exception:
            await app.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)
    else:
        await app.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)

@call.on_stream_end()
async def stream_end_handler(chat_id: int):
    await play_next(chat_id)

# ============================================================
# 🛠️ ADMIN TOOLS (BAN, UNBAN, MUTE, UNMUTE, WARN, WELCOME, PROMOTE, DEMOTE)
# ============================================================

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# --- 1. /ban ---
@app.on_message(filters.command("ban") & filters.group)
async def ban_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to ban them.")
    user_id = message.reply_to_message.from_user.id
    try:
        await app.ban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ <b>Banned</b> <a href='tg://user?id={user_id}'>User</a> successfully.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 2. /unban ---
@app.on_message(filters.command("unban") & filters.group)
async def unban_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    try:
        user_id = int(message.command[1]) if len(message.command) > 1 else None
        if not user_id:
            return await message.reply("❌ Usage: `/unban user_id`")
        await app.unban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ <b>Unbanned</b> User ID: `{user_id}`", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 3. /mute ---
@app.on_message(filters.command("mute") & filters.group)
async def mute_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to mute them.")
    user_id = message.reply_to_message.from_user.id
    try:
        await app.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
        await message.reply(f"🔇 <b>Muted</b> <a href='tg://user?id={user_id}'>User</a> permanently.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 4. /unmute ---
@app.on_message(filters.command("unmute") & filters.group)
async def unmute_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to unmute them.")
    user_id = message.reply_to_message.from_user.id
    try:
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )
        await app.restrict_chat_member(message.chat.id, user_id, perms)
        await message.reply(f"🔊 <b>Unmuted</b> <a href='tg://user?id={user_id}'>User</a>.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 5. /warn ---
@app.on_message(filters.command("warn") & filters.group)
async def warn_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to warn them.")
    chat_id = str(message.chat.id)
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    if chat_id not in warnings:
        warnings[chat_id] = {}
    warnings[chat_id][str(user_id)] = warnings[chat_id].get(str(user_id), 0) + 1
    count = warnings[chat_id][str(user_id)]
    update_db()
    await message.reply(f"⚠️ <b>Warning!</b> {target} has been warned.\n📊 <b>Total Warnings:</b> `{count}`/3", parse_mode="html")
    if count >= 3:
        try:
            await app.ban_chat_member(message.chat.id, user_id)
            await message.reply(f"🚫 {target} has been <b>banned</b> for exceeding 3 warnings!", parse_mode="html")
            warnings[chat_id][str(user_id)] = 0
            update_db()
        except Exception as e:
            await message.reply(f"❌ Auto-ban failed: {e}")

# --- 6. /unwarn ---
@app.on_message(filters.command("unwarn") & filters.group)
async def unwarn_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to unwarn them.")
    chat_id = str(message.chat.id)
    user_id = str(message.reply_to_message.from_user.id)
    target = message.reply_to_message.from_user.mention
    if chat_id in warnings and user_id in warnings[chat_id] and warnings[chat_id][user_id] > 0:
        warnings[chat_id][user_id] -= 1
        new_count = warnings[chat_id][user_id]
        update_db()
        await message.reply(f"✅ Removed 1 warning from {target}.\n📊 <b>Remaining Warnings:</b> `{new_count}`", parse_mode="html")
    else:
        await message.reply(f"ℹ️ {target} has no warnings to remove.", parse_mode="html")

# --- 7. /warns ---
@app.on_message(filters.command("warns") & filters.group)
async def warns_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        user_id = str(message.from_user.id)
        count = warnings.get(chat_id, {}).get(user_id, 0)
        await message.reply(f"📊 <b>Your Warnings:</b> `{count}`", parse_mode="html")
    else:
        if not await is_admin(message.chat.id, message.from_user.id):
            return await message.reply("❌ Only admins can check others' warnings.")
        user_id = str(message.reply_to_message.from_user.id)
        target = message.reply_to_message.from_user.mention
        count = warnings.get(chat_id, {}).get(user_id, 0)
        await message.reply(f"📊 <b>Warnings for {target}:</b> `{count}`", parse_mode="html")

# --- 8. /setwelcome ---
@app.on_message(filters.command("setwelcome") & filters.group)
async def setwelcome_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    chat_id = str(message.chat.id)
    if message.reply_to_message:
        if message.reply_to_message.text:
            welcome_msgs[chat_id] = message.reply_to_message.text
        elif message.reply_to_message.caption:
            welcome_msgs[chat_id] = message.reply_to_message.caption
        else:
            return await message.reply("❌ Please reply to a text message.")
    else:
        if len(message.command) < 2:
            return await message.reply("❌ Usage: `/setwelcome Welcome to the group!` or reply to a message.")
        welcome_msgs[chat_id] = " ".join(message.command[1:])
    update_db()
    await message.reply(f"✅ <b>Welcome message set successfully!</b>\n\n`{welcome_msgs[chat_id]}`", parse_mode="html")

# --- 9. /delwelcome ---
@app.on_message(filters.command("delwelcome") & filters.group)
async def delwelcome_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    chat_id = str(message.chat.id)
    if chat_id in welcome_msgs:
        del welcome_msgs[chat_id]
        update_db()
        await message.reply("✅ <b>Welcome message deleted.</b>", parse_mode="html")
    else:
        await message.reply("ℹ️ No welcome message set.", parse_mode="html")

# --- 10. /promote ---
@app.on_message(filters.command("promote") & filters.group)
async def promote_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to promote them.")
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    try:
        await app.promote_chat_member(
            message.chat.id,
            user_id,
            can_manage_chat=True,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_restrict_members=False,
            can_promote_members=False
        )
        await message.reply(f"✅ <b>Promoted</b> {target} to admin (without ban/promote rights).", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 11. /demote ---
@app.on_message(filters.command("demote") & filters.group)
async def demote_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to demote them.")
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    try:
        await app.promote_chat_member(
            message.chat.id,
            user_id,
            can_manage_chat=False,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_restrict_members=False,
            can_promote_members=False
        )
        await message.reply(f"✅ <b>Demoted</b> {target} to normal member.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# ============================================================
# 👋 WELCOME HANDLER
# ============================================================

@app.on_message(filters.group & filters.new_chat_members)
async def welcome_new_member(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if chat_id in welcome_msgs:
        for member in message.new_chat_members:
            if member.id == (await app.get_me()).id:
                continue
            welcome_text = welcome_msgs[chat_id]
            welcome_text = welcome_text.replace("{name}", member.mention)
            welcome_text = welcome_text.replace("{username}", f"@{member.username}" if member.username else "No Username")
            await message.reply(welcome_text, parse_mode="html")
            break

# ============================================================
# 🎮 MUSIC COMMANDS
# ============================================================

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    intro_text = (
        "<b>✧･ﾟ: *✧･ﾟ:*  𝐕𝐀𝐍𝐈𝐗 𝐌𝐔𝐒𝐈𝐂  *:･ﾟ✧*:･ﾟ✧</b>\n"
        "<b>     ⋆⋅☆⋅⋆  Premium Edition  ⋆⋅☆⋅⋆</b>\n\n"
        "<b>✦ Telegram's smoothest bot for VC audio & video playback</b>\n\n"
        "<b>🎧 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬</b>\n"
        "➤ <b>𝐇𝐃 𝐀𝐮𝐝𝐢𝐨</b> - Crystal-clear sound\n"
        "➤ <b>𝐇𝐃 𝐕𝐢𝐝𝐞𝐨</b> - Perfect playback\n"
        "➤ <b>𝐋𝐨𝐠-𝐅𝐫𝐞𝐞</b> - Zero tracking, fully private\n"
        "➤ <b>𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝 𝐐𝐮𝐞𝐮𝐞</b> - Smooth management\n"
        "➤ <b>𝐀𝐝𝐦𝐢𝐧 𝐓𝐨𝐨𝐥𝐬</b> - Ban, Mute, Warn, Promote\n"
        "➤ <b>𝐙𝐞𝐫𝐨-𝐋𝐚𝐠 𝐂𝐨𝐫𝐞</b> - Feels fast & easy\n\n"
        "<b>🚀 𝐐𝐮𝐢𝐜𝐤 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬</b>\n"
        "➤ <code>/play &lt;song&gt;</code> - Play audio in VC\n"
        "➤ <code>/vplay &lt;song&gt;</code> - Stream video (Screen-share)\n"
        "➤ <code>/pause | /resume | /skip | /stop | /loop | /queue</code>\n\n"
        "<b>🛠️ 𝐀𝐝𝐦𝐢𝐧 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬</b>\n"
        "➤ <code>/ban | /unban | /mute | /unmute</code>\n"
        "➤ <code>/warn | /unwarn | /warns</code>\n"
        "➤ <code>/promote | /demote</code>\n"
        "➤ <code>/setwelcome | /delwelcome</code>\n\n"
        "<b>📢 𝐀𝐝𝐝 𝐦𝐞 𝐭𝐨 𝐲𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩 𝐚𝐧𝐝 𝐞𝐧𝐣𝐨𝐲!</b>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐀𝐝𝐝 𝐭𝐨 𝐆𝐫𝐨𝐮𝐩", url="https://t.me/vanixmusic_bot?startgroup=true")],
        [
            InlineKeyboardButton("💬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url="https://t.me/vanixsupport"),
            InlineKeyboardButton("👨‍💻 𝐎𝐰𝐧𝐞𝐫", url="https://t.me/vanixowner"),
            InlineKeyboardButton("🧑‍💻 𝐂𝐫𝐞𝐚𝐭𝐨𝐫", url="https://t.me/vanixcreator"),
        ]
    ])
    await message.reply(intro_text, parse_mode="html", disable_web_page_preview=True, reply_markup=keyboard)

@app.on_message(filters.command(["play", "p"]))
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/play &lt;song name or link&gt;</code>", parse_mode="html")
        return
    
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 <b>Searching audio...</b>", parse_mode="html")
    
    try:
        song_info = await get_audio_info(query)
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> <code>{str(e)}</code>", parse_mode="html")
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    
    try:
        await call.stop_stream(chat_id)
    except:
        pass

    if not current_track.get(chat_id):
        queues[chat_id].append(song_info)
        duration = song_info.get('duration_str', 'Unknown')
        now_playing_text = (
            f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n"
            f"<b>   ⋆⋅☆⋅⋆  𝐍𝐎𝐖 𝐏𝐋𝐀𝐘𝐈𝐍𝐆  ⋆⋅☆⋅⋆</b>\n"
            f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n\n"
            f"<b>🎵 Title:</b> <a href='{song_info['webpage_url']}'>{song_info['title']}</a>\n"
            f"<b>⏱ Duration:</b> <code>{duration}</code>\n"
            f"<b>👤 Uploader:</b> {song_info.get('uploader', 'Unknown')}\n"
            f"<b>👀 Views:</b> {song_info.get('view_count', 0):,}\n\n"
            f"<b>📊 Queue:</b> <code>{len(queues.get(chat_id, []))}</code> songs remaining"
        )
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ 𝐏𝐚𝐮𝐬𝐞", callback_data="pause"),
                InlineKeyboardButton("▶️ 𝐑𝐞𝐬𝐮𝐦𝐞", callback_data="resume"),
            ],
            [
                InlineKeyboardButton("⏭ 𝐒𝐤𝐢𝐩", callback_data="skip"),
                InlineKeyboardButton("🔁 𝐋𝐨𝐨𝐩", callback_data="loop"),
            ],
            [
                InlineKeyboardButton("⏹ 𝐒𝐭𝐨𝐩", callback_data="stop"),
                InlineKeyboardButton("📋 𝐐𝐮𝐞𝐮𝐞", callback_data="queue"),
            ]
        ])
        if song_info.get('thumbnail'):
            try:
                await app.send_photo(chat_id, photo=song_info['thumbnail'], caption=now_playing_text, reply_markup=keyboard, parse_mode="html")
                await msg.delete()
            except Exception:
                await msg.edit(now_playing_text, reply_markup=keyboard, parse_mode="html")
        else:
            await msg.edit(now_playing_text, reply_markup=keyboard, parse_mode="html")
        await play_next(chat_id)
    else:
        position = len(queues[chat_id]) + 1
        queues[chat_id].append(song_info)
        await msg.edit(
            f"✅ <b>{song_info['title']}</b> added to queue.\n"
            f"📊 <b>Position:</b> <code>{position}</code>",
            parse_mode="html"
        )

@app.on_message(filters.command(["vplay", "vp"]))
async def vplay_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/vplay &lt;song or video name&gt;</code>", parse_mode="html")
        return
    
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 <b>Searching video...</b>", parse_mode="html")
    
    try:
        video_info = await get_video_info(query)
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> <code>{str(e)}</code>", parse_mode="html")
        return
    
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    
    try:
        await call.leave_call(chat_id)
    except:
        pass
    
    try:
        await call.join_call(chat_id, stream=VideoStream(video_info['url']))
        await msg.edit(
            f"<b>✧･ﾟ: *✧･ﾟ:*  📺 𝐍𝐎𝐖 𝐕𝐈𝐃𝐄𝐎 𝐒𝐓𝐑𝐄𝐀𝐌𝐈𝐍𝐆  *:･ﾟ✧*:･ﾟ✧</b>\n\n"
            f"<b>🎬 Title:</b> <a href='{video_info['webpage_url']}'>{video_info['title']}</a>\n"
            f"<b>⏱ Duration:</b> <code>{video_info['duration_str']}</code>\n\n"
            f"<b>💡 Note:</b> Make sure <b>Video Call</b> is active in the group!",
            parse_mode="html",
            disable_web_page_preview=True
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏸ Pause Video", callback_data="vpause"),
             InlineKeyboardButton("▶️ Resume Video", callback_data="vresume")],
            [InlineKeyboardButton("⏹ Stop Stream", callback_data="vstop")]
        ])
        await app.send_message(chat_id, "🎛 Stream Controls:", reply_markup=keyboard)
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> <code>{str(e)}</code>\n\nMake sure you have started a <b>Video Call</b> in the group first!", parse_mode="html")

@app.on_message(filters.command("pause"))
async def pause_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.pause_stream(chat_id)
        await message.reply("⏸ <b>Paused</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

@app.on_message(filters.command("resume"))
async def resume_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.resume_stream(chat_id)
        await message.reply("▶️ <b>Resumed</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

@app.on_message(filters.command(["skip", "next"]))
async def skip_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not current_track.get(chat_id):
        await message.reply("❌ Nothing is playing.", parse_mode="html")
        return
    current_track[chat_id] = {}
    try:
        await call.stop_stream(chat_id)
    except:
        pass
    await play_next(chat_id)
    await message.reply("⏭ <b>Skipped</b>", parse_mode="html")

@app.on_message(filters.command(["stop", "end"]))
async def stop_command(client: Client, message: Message):
    chat_id = message.chat.id
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    try:
        await call.leave_call(chat_id)
        await message.reply("⏹ <b>Stopped and left VC</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

@app.on_message(filters.command("loop"))
async def loop_command(client: Client, message: Message):
    chat_id = message.chat.id
    current = loop_status.get(chat_id, False)
    loop_status[chat_id] = not current
    status = "𝑶𝑵 🔁" if loop_status[chat_id] else "𝑶𝑭𝑭 ➡️"
    await message.reply(f"🔄 <b>Loop:</b> <code>{status}</code>", parse_mode="html")

@app.on_message(filters.command(["queue", "q"]))
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not queues.get(chat_id) and not current_track.get(chat_id):
        await message.reply("📭 Queue is empty", parse_mode="html")
        return
    text = "<b>✦ 𝗤𝗨𝗘𝗨𝗘 𝗟𝗜𝗦𝗧 ✦</b>\n\n"
    if current_track.get(chat_id):
        text += f"<b>▶️ Now Playing:</b>\n   {current_track[chat_id]['title']}\n   ⏱ <code>{current_track[chat_id]['duration_str']}</code>\n\n"
    if queues.get(chat_id):
        text += "<b>Up Next:</b>\n"
        for i, song in enumerate(queues[chat_id][:15], 1):
            text += f"<code>{i}.</code> {song['title']} <code>[{song['duration_str']}]</code>\n"
        if len(queues[chat_id]) > 15:
            text += f"\n... and <code>{len(queues[chat_id])-15}</code> more"
    await message.reply(text, parse_mode="html")

@app.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = datetime.now()
    msg = await message.reply("🏓 <b>Pinging...</b>", parse_mode="html")
    end = datetime.now()
    latency = (end - start).microseconds / 1000
    await msg.edit(f"🏓 <b>Pong!</b>\n⚡ <b>Latency:</b> <code>{latency:.2f}ms</code>", parse_mode="html")

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply(
        f"<b>✧･ﾟ: *✧･ﾟ:*  𝑽𝑨𝑵𝑰𝑿 𝑴𝑼𝑺𝑰𝑪 𝑩𝑶𝑻  *:･ﾟ✧*:･ﾟ✧</b>\n\n"
        f"<b>🎯 𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔</b>\n"
        f"➤ <code>/play &lt;song&gt;</code> - Play audio\n"
        f"➤ <code>/vplay &lt;song&gt;</code> - Stream video\n"
        f"➤ <code>/pause</code> - Pause\n"
        f"➤ <code>/resume</code> - Resume\n"
        f"➤ <code>/skip</code> - Skip\n"
        f"➤ <code>/stop</code> - Stop & clear queue\n"
        f"➤ <code>/loop</code> - Toggle loop\n"
        f"➤ <code>/queue</code> - View queue\n"
        f"➤ <code>/ping</code> - Check status\n\n"
        f"<b>🛠️ Admin:</b> /ban, /unban, /mute, /unmute, /warn, /unwarn, /warns, /promote, /demote, /setwelcome, /delwelcome\n\n"
        f"<b>📢 Support:</b> @vanixsupport\n"
        f"<b>👨‍💻 Owner:</b> @vanixowner\n"
        f"<b>🧑‍💻 Creator:</b> @vanixcreator",
        parse_mode="html"
    )

# ============================================================
# 🔘 INLINE BUTTONS CALLBACK HANDLER
# ============================================================

@app.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    data = callback.data
    
    if data == "pause":
        try:
            await call.pause_stream(chat_id)
            await callback.answer("⏸ Paused", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "resume":
        try:
            await call.resume_stream(chat_id)
            await callback.answer("▶️ Resumed", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "skip":
        if current_track.get(chat_id):
            current_track[chat_id] = {}
            try:
                await call.stop_stream(chat_id)
            except:
                pass
            await play_next(chat_id)
            await callback.answer("⏭ Skipped", show_alert=True)
        else:
            await callback.answer("Nothing playing", show_alert=True)
    elif data == "loop":
        current = loop_status.get(chat_id, False)
        loop_status[chat_id] = not current
        await callback.answer(f"Loop: {'ON' if loop_status[chat_id] else 'OFF'}", show_alert=True)
    elif data == "stop":
        queues[chat_id] = []
        current_track[chat_id] = {}
        loop_status[chat_id] = False
        try:
            await call.leave_call(chat_id)
            await callback.answer("⏹ Stopped", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
        await callback.message.delete()
    elif data == "queue":
        if not queues.get(chat_id) and not current_track.get(chat_id):
            await callback.answer("Queue is empty", show_alert=True)
            return
        text = "✦ 𝗤𝗨𝗘𝗨𝗘 ✦\n\n"
        if current_track.get(chat_id):
            text += f"▶️ Now: {current_track[chat_id]['title']}\n"
        if queues.get(chat_id):
            text += "\nUp Next:\n"
            for i, song in enumerate(queues[chat_id][:10], 1):
                text += f"{i}. {song['title']}\n"
        await callback.answer(text[:200], show_alert=True)
    elif data == "vpause":
        try:
            await call.pause_stream(chat_id)
            await callback.answer("⏸ Video Paused", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "vresume":
        try:
            await call.resume_stream(chat_id)
            await callback.answer("▶️ Video Resumed", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "vstop":
        try:
            await call.leave_call(chat_id)
            queues[chat_id] = []
            current_track[chat_id] = {}
            await callback.answer("⏹ Video Stream Stopped", show_alert=True)
            await callback.message.delete()
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)

# ============================================================
# 🚀 BOT LAUNCH
# ============================================================

async def main():
    print("""
    ✧･ﾟ: *✧･ﾟ:*  VΛПIΧ  MЦSIC  BӨƬ  *:･ﾟ✧*:･ﾟ✧
       ──── ⋆⋅☆⋅⋆ ──── ⋆⋅☆⋅⋆ ──── 
        ✦  P R E M I U M   E D I T I O N  ✦
       ──── ⋆⋅☆⋅⋆ ──── ⋆⋅☆⋅⋆ ────
    """)
    
    await app.start()
    await call.start()
    
    print(f"✅ Bot is running as {BOT_USERNAME}")
    print("📊 Commands: /play (Audio), /vplay (Video), /ban, /mute, /warn, /promote, /demote, /setwelcome")
    print("🤖 Press Ctrl+C to stop")
    
    await idle()

if __name__ == "__main__":
    asyncio.run(main())(chat_id: int, song: dict):
    """Now Playing with Thumbnail + Fancy Formatting"""
    duration = song.get('duration_str', 'Unknown')
    text = (
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n"
        f"<b>   ⋆⋅☆⋅⋆  𝐍𝐎𝐖 𝐏𝐋𝐀𝐘𝐈𝐍𝐆  ⋆⋅☆⋅⋆</b>\n"
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n\n"
        f"<b>🎵 𝐓𝐢𝐭𝐥𝐞:</b> <a href='{song['webpage_url']}'>{song['title']}</a>\n"
        f"<b>⏱ 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧:</b> <code>{duration}</code>\n"
        f"<b>👤 𝐔𝐩𝐥𝐨𝐚𝐝𝐞𝐫:</b> {song.get('uploader', 'Unknown')}\n"
        f"<b>👀 𝐕𝐢𝐞𝐰𝐬:</b> {song.get('view_count', 0):,}\n\n"
        f"<b>📊 𝐐𝐮𝐞𝐮𝐞:</b> <code>{len(queues.get(chat_id, []))}</code> songs remaining"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ 𝐏𝐚𝐮𝐬𝐞", callback_data="pause"),
            InlineKeyboardButton("▶️ 𝐑𝐞𝐬𝐮𝐦𝐞", callback_data="resume"),
        ],
        [
            InlineKeyboardButton("⏭ 𝐒𝐤𝐢𝐩", callback_data="skip"),
            InlineKeyboardButton("🔁 𝐋𝐨𝐨𝐩", callback_data="loop"),
        ],
        [
            InlineKeyboardButton("⏹ 𝐒𝐭𝐨𝐩", callback_data="stop"),
            InlineKeyboardButton("📋 𝐐𝐮𝐞𝐮𝐞", callback_data="queue"),
        ]
    ])
    if song.get('thumbnail'):
        try:
            await app.send_photo(chat_id, photo=song['thumbnail'], caption=text, reply_markup=keyboard, parse_mode="html")
        except Exception:
            await app.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)
    else:
        await app.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)

@call.on_stream_end()
async def stream_end_handler(chat_id: int):
    await play_next(chat_id)

# ============================================================
# 🛠️ ADMIN TOOLS (BAN, UNBAN, MUTE, UNMUTE, WARN, WELCOME, PROMOTE, DEMOTE)
# ============================================================

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# --- 1. /ban ---
@app.on_message(filters.command("ban") & filters.group)
async def ban_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to ban them.")
    user_id = message.reply_to_message.from_user.id
    try:
        await app.ban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ <b>Banned</b> <a href='tg://user?id={user_id}'>User</a> successfully.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 2. /unban ---
@app.on_message(filters.command("unban") & filters.group)
async def unban_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    try:
        user_id = int(message.command[1]) if len(message.command) > 1 else None
        if not user_id:
            return await message.reply("❌ Usage: `/unban user_id`")
        await app.unban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ <b>Unbanned</b> User ID: `{user_id}`", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 3. /mute ---
@app.on_message(filters.command("mute") & filters.group)
async def mute_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to mute them.")
    user_id = message.reply_to_message.from_user.id
    try:
        await app.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
        await message.reply(f"🔇 <b>Muted</b> <a href='tg://user?id={user_id}'>User</a> permanently.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 4. /unmute ---
@app.on_message(filters.command("unmute") & filters.group)
async def unmute_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to unmute them.")
    user_id = message.reply_to_message.from_user.id
    try:
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_change_info=True,
            can_invite_users=True,
            can_pin_messages=True
        )
        await app.restrict_chat_member(message.chat.id, user_id, perms)
        await message.reply(f"🔊 <b>Unmuted</b> <a href='tg://user?id={user_id}'>User</a>.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 5. /warn ---
@app.on_message(filters.command("warn") & filters.group)
async def warn_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to warn them.")
    chat_id = str(message.chat.id)
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    if chat_id not in warnings:
        warnings[chat_id] = {}
    warnings[chat_id][str(user_id)] = warnings[chat_id].get(str(user_id), 0) + 1
    count = warnings[chat_id][str(user_id)]
    update_db()
    await message.reply(f"⚠️ <b>Warning!</b> {target} has been warned.\n📊 <b>Total Warnings:</b> `{count}`/3", parse_mode="html")
    if count >= 3:
        try:
            await app.ban_chat_member(message.chat.id, user_id)
            await message.reply(f"🚫 {target} has been <b>banned</b> for exceeding 3 warnings!", parse_mode="html")
            warnings[chat_id][str(user_id)] = 0
            update_db()
        except Exception as e:
            await message.reply(f"❌ Auto-ban failed: {e}")

# --- 6. /unwarn ---
@app.on_message(filters.command("unwarn") & filters.group)
async def unwarn_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to unwarn them.")
    chat_id = str(message.chat.id)
    user_id = str(message.reply_to_message.from_user.id)
    target = message.reply_to_message.from_user.mention
    if chat_id in warnings and user_id in warnings[chat_id] and warnings[chat_id][user_id] > 0:
        warnings[chat_id][user_id] -= 1
        new_count = warnings[chat_id][user_id]
        update_db()
        await message.reply(f"✅ Removed 1 warning from {target}.\n📊 <b>Remaining Warnings:</b> `{new_count}`", parse_mode="html")
    else:
        await message.reply(f"ℹ️ {target} has no warnings to remove.", parse_mode="html")

# --- 7. /warns ---
@app.on_message(filters.command("warns") & filters.group)
async def warns_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        user_id = str(message.from_user.id)
        count = warnings.get(chat_id, {}).get(user_id, 0)
        await message.reply(f"📊 <b>Your Warnings:</b> `{count}`", parse_mode="html")
    else:
        if not await is_admin(message.chat.id, message.from_user.id):
            return await message.reply("❌ Only admins can check others' warnings.")
        user_id = str(message.reply_to_message.from_user.id)
        target = message.reply_to_message.from_user.mention
        count = warnings.get(chat_id, {}).get(user_id, 0)
        await message.reply(f"📊 <b>Warnings for {target}:</b> `{count}`", parse_mode="html")

# --- 8. /setwelcome ---
@app.on_message(filters.command("setwelcome") & filters.group)
async def setwelcome_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    chat_id = str(message.chat.id)
    if message.reply_to_message:
        if message.reply_to_message.text:
            welcome_msgs[chat_id] = message.reply_to_message.text
        elif message.reply_to_message.caption:
            welcome_msgs[chat_id] = message.reply_to_message.caption
        else:
            return await message.reply("❌ Please reply to a text message.")
    else:
        if len(message.command) < 2:
            return await message.reply("❌ Usage: `/setwelcome Welcome to the group!` or reply to a message.")
        welcome_msgs[chat_id] = " ".join(message.command[1:])
    update_db()
    await message.reply(f"✅ <b>Welcome message set successfully!</b>\n\n`{welcome_msgs[chat_id]}`", parse_mode="html")

# --- 9. /delwelcome ---
@app.on_message(filters.command("delwelcome") & filters.group)
async def delwelcome_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    chat_id = str(message.chat.id)
    if chat_id in welcome_msgs:
        del welcome_msgs[chat_id]
        update_db()
        await message.reply("✅ <b>Welcome message deleted.</b>", parse_mode="html")
    else:
        await message.reply("ℹ️ No welcome message set.", parse_mode="html")

# --- 10. /promote ---
@app.on_message(filters.command("promote") & filters.group)
async def promote_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to promote them.")
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    try:
        await app.promote_chat_member(
            message.chat.id,
            user_id,
            can_manage_chat=True,
            can_change_info=True,
            can_delete_messages=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_restrict_members=False,
            can_promote_members=False
        )
        await message.reply(f"✅ <b>Promoted</b> {target} to admin (without ban/promote rights).", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# --- 11. /demote ---
@app.on_message(filters.command("demote") & filters.group)
async def demote_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to demote them.")
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    try:
        await app.promote_chat_member(
            message.chat.id,
            user_id,
            can_manage_chat=False,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_pin_messages=False,
            can_restrict_members=False,
            can_promote_members=False
        )
        await message.reply(f"✅ <b>Demoted</b> {target} to normal member.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# ============================================================
# 👋 WELCOME HANDLER
# ============================================================

@app.on_message(filters.group & filters.new_chat_members)
async def welcome_new_member(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if chat_id in welcome_msgs:
        for member in message.new_chat_members:
            if member.id == (await app.get_me()).id:
                continue
            welcome_text = welcome_msgs[chat_id]
            welcome_text = welcome_text.replace("{name}", member.mention)
            welcome_text = welcome_text.replace("{username}", f"@{member.username}" if member.username else "No Username")
            await message.reply(welcome_text, parse_mode="html")
            break

# ============================================================
# 🎮 MUSIC COMMANDS
# ============================================================

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    intro_text = (
        "<b>✧･ﾟ: *✧･ﾟ:*  𝐕𝐀𝐍𝐈𝐗 𝐌𝐔𝐒𝐈𝐂  *:･ﾟ✧*:･ﾟ✧</b>\n"
        "<b>     ⋆⋅☆⋅⋆  Premium Edition  ⋆⋅☆⋅⋆</b>\n\n"
        "<b>✦ Telegram's smoothest bot for VC audio & video playback</b>\n\n"
        "<b>🎧 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬</b>\n"
        "➤ <b>𝐇𝐃 𝐀𝐮𝐝𝐢𝐨</b> - Crystal-clear sound\n"
        "➤ <b>𝐇𝐃 𝐕𝐢𝐝𝐞𝐨</b> - Perfect playback\n"
        "➤ <b>𝐋𝐨𝐠-𝐅𝐫𝐞𝐞</b> - Zero tracking, fully private\n"
        "➤ <b>𝐀𝐝𝐯𝐚𝐧𝐜𝐞𝐝 𝐐𝐮𝐞𝐮𝐞</b> - Smooth management\n"
        "➤ <b>𝐀𝐝𝐦𝐢𝐧 𝐓𝐨𝐨𝐥𝐬</b> - Ban, Mute, Warn, Promote\n"
        "➤ <b>𝐙𝐞𝐫𝐨-𝐋𝐚𝐠 𝐂𝐨𝐫𝐞</b> - Feels fast & easy\n\n"
        "<b>🚀 𝐐𝐮𝐢𝐜𝐤 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬</b>\n"
        "➤ <code>/play &lt;song&gt;</code> - Play audio in VC\n"
        "➤ <code>/vplay &lt;song&gt;</code> - Stream video (Screen-share)\n"
        "➤ <code>/pause | /resume | /skip | /stop | /loop | /queue</code>\n\n"
        "<b>🛠️ 𝐀𝐝𝐦𝐢𝐧 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬</b>\n"
        "➤ <code>/ban | /unban | /mute | /unmute</code>\n"
        "➤ <code>/warn | /unwarn | /warns</code>\n"
        "➤ <code>/promote | /demote</code>\n"
        "➤ <code>/setwelcome | /delwelcome</code>\n\n"
        "<b>📢 𝐀𝐝𝐝 𝐦𝐞 𝐭𝐨 𝐲𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩 𝐚𝐧𝐝 𝐞𝐧𝐣𝐨𝐲!</b>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 𝐀𝐝𝐝 𝐭𝐨 𝐆𝐫𝐨𝐮𝐩", url="https://t.me/vanixmusic_bot?startgroup=true")],
        [
            InlineKeyboardButton("💬 𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url="https://t.me/vanixsupport"),
            InlineKeyboardButton("👨‍💻 𝐎𝐰𝐧𝐞𝐫", url="https://t.me/vanixowner"),
            InlineKeyboardButton("🧑‍💻 𝐂𝐫𝐞𝐚𝐭𝐨𝐫", url="https://t.me/vanixcreator"),
        ]
    ])
    await message.reply(intro_text, parse_mode="html", disable_web_page_preview=True, reply_markup=keyboard)

@app.on_message(filters.command(["play", "p"]))
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/play &lt;song name or link&gt;</code>", parse_mode="html")
        return
    
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 <b>Searching audio...</b>", parse_mode="html")
    
    try:
        song_info = await get_audio_info(query)
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> <code>{str(e)}</code>", parse_mode="html")
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    
    try:
        await call.stop_stream(chat_id)
    except:
        pass

    if not current_track.get(chat_id):
        queues[chat_id].append(song_info)
        duration = song_info.get('duration_str', 'Unknown')
        now_playing_text = (
            f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n"
            f"<b>   ⋆⋅☆⋅⋆  𝐍𝐎𝐖 𝐏𝐋𝐀𝐘𝐈𝐍𝐆  ⋆⋅☆⋅⋆</b>\n"
            f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n\n"
            f"<b>🎵 Title:</b> <a href='{song_info['webpage_url']}'>{song_info['title']}</a>\n"
            f"<b>⏱ Duration:</b> <code>{duration}</code>\n"
            f"<b>👤 Uploader:</b> {song_info.get('uploader', 'Unknown')}\n"
            f"<b>👀 Views:</b> {song_info.get('view_count', 0):,}\n\n"
            f"<b>📊 Queue:</b> <code>{len(queues.get(chat_id, []))}</code> songs remaining"
        )
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ 𝐏𝐚𝐮𝐬𝐞", callback_data="pause"),
                InlineKeyboardButton("▶️ 𝐑𝐞𝐬𝐮𝐦𝐞", callback_data="resume"),
            ],
            [
                InlineKeyboardButton("⏭ 𝐒𝐤𝐢𝐩", callback_data="skip"),
                InlineKeyboardButton("🔁 𝐋𝐨𝐨𝐩", callback_data="loop"),
            ],
            [
                InlineKeyboardButton("⏹ 𝐒𝐭𝐨𝐩", callback_data="stop"),
                InlineKeyboardButton("📋 𝐐𝐮𝐞𝐮𝐞", callback_data="queue"),
            ]
        ])
        if song_info.get('thumbnail'):
            try:
                await app.send_photo(chat_id, photo=song_info['thumbnail'], caption=now_playing_text, reply_markup=keyboard, parse_mode="html")
                await msg.delete()
            except Exception:
                await msg.edit(now_playing_text, reply_markup=keyboard, parse_mode="html")
        else:
            await msg.edit(now_playing_text, reply_markup=keyboard, parse_mode="html")
        await play_next(chat_id)
    else:
        position = len(queues[chat_id]) + 1
        queues[chat_id].append(song_info)
        await msg.edit(
            f"✅ <b>{song_info['title']}</b> added to queue.\n"
            f"📊 <b>Position:</b> <code>{position}</code>",
            parse_mode="html"
        )

@app.on_message(filters.command(["vplay", "vp"]))
async def vplay_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/vplay &lt;song or video name&gt;</code>", parse_mode="html")
        return
    
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 <b>Searching video...</b>", parse_mode="html")
    
    try:
        video_info = await get_video_info(query)
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> <code>{str(e)}</code>", parse_mode="html")
        return
    
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    
    try:
        await call.leave_call(chat_id)
    except:
        pass
    
    try:
        await call.join_call(chat_id, stream=VideoStream(video_info['url']))
        await msg.edit(
            f"<b>✧･ﾟ: *✧･ﾟ:*  📺 𝐍𝐎𝐖 𝐕𝐈𝐃𝐄𝐎 𝐒𝐓𝐑𝐄𝐀𝐌𝐈𝐍𝐆  *:･ﾟ✧*:･ﾟ✧</b>\n\n"
            f"<b>🎬 Title:</b> <a href='{video_info['webpage_url']}'>{video_info['title']}</a>\n"
            f"<b>⏱ Duration:</b> <code>{video_info['duration_str']}</code>\n\n"
            f"<b>💡 Note:</b> Make sure <b>Video Call</b> is active in the group!",
            parse_mode="html",
            disable_web_page_preview=True
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⏸ Pause Video", callback_data="vpause"),
             InlineKeyboardButton("▶️ Resume Video", callback_data="vresume")],
            [InlineKeyboardButton("⏹ Stop Stream", callback_data="vstop")]
        ])
        await app.send_message(chat_id, "🎛 Stream Controls:", reply_markup=keyboard)
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> <code>{str(e)}</code>\n\nMake sure you have started a <b>Video Call</b> in the group first!", parse_mode="html")

@app.on_message(filters.command("pause"))
async def pause_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.pause_stream(chat_id)
        await message.reply("⏸ <b>Paused</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

@app.on_message(filters.command("resume"))
async def resume_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.resume_stream(chat_id)
        await message.reply("▶️ <b>Resumed</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

@app.on_message(filters.command(["skip", "next"]))
async def skip_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not current_track.get(chat_id):
        await message.reply("❌ Nothing is playing.", parse_mode="html")
        return
    current_track[chat_id] = {}
    try:
        await call.stop_stream(chat_id)
    except:
        pass
    await play_next(chat_id)
    await message.reply("⏭ <b>Skipped</b>", parse_mode="html")

@app.on_message(filters.command(["stop", "end"]))
async def stop_command(client: Client, message: Message):
    chat_id = message.chat.id
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    try:
        await call.leave_call(chat_id)
        await message.reply("⏹ <b>Stopped and left VC</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

@app.on_message(filters.command("loop"))
async def loop_command(client: Client, message: Message):
    chat_id = message.chat.id
    current = loop_status.get(chat_id, False)
    loop_status[chat_id] = not current
    status = "𝑶𝑵 🔁" if loop_status[chat_id] else "𝑶𝑭𝑭 ➡️"
    await message.reply(f"🔄 <b>Loop:</b> <code>{status}</code>", parse_mode="html")

@app.on_message(filters.command(["queue", "q"]))
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not queues.get(chat_id) and not current_track.get(chat_id):
        await message.reply("📭 Queue is empty", parse_mode="html")
        return
    text = "<b>✦ 𝗤𝗨𝗘𝗨𝗘 𝗟𝗜𝗦𝗧 ✦</b>\n\n"
    if current_track.get(chat_id):
        text += f"<b>▶️ Now Playing:</b>\n   {current_track[chat_id]['title']}\n   ⏱ <code>{current_track[chat_id]['duration_str']}</code>\n\n"
    if queues.get(chat_id):
        text += "<b>Up Next:</b>\n"
        for i, song in enumerate(queues[chat_id][:15], 1):
            text += f"<code>{i}.</code> {song['title']} <code>[{song['duration_str']}]</code>\n"
        if len(queues[chat_id]) > 15:
            text += f"\n... and <code>{len(queues[chat_id])-15}</code> more"
    await message.reply(text, parse_mode="html")

@app.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = datetime.now()
    msg = await message.reply("🏓 <b>Pinging...</b>", parse_mode="html")
    end = datetime.now()
    latency = (end - start).microseconds / 1000
    await msg.edit(f"🏓 <b>Pong!</b>\n⚡ <b>Latency:</b> <code>{latency:.2f}ms</code>", parse_mode="html")

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply(
        f"<b>✧･ﾟ: *✧･ﾟ:*  𝑽𝑨𝑵𝑰𝑿 𝑴𝑼𝑺𝑰𝑪 𝑩𝑶𝑻  *:･ﾟ✧*:･ﾟ✧</b>\n\n"
        f"<b>🎯 𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔</b>\n"
        f"➤ <code>/play &lt;song&gt;</code> - Play audio\n"
        f"➤ <code>/vplay &lt;song&gt;</code> - Stream video\n"
        f"➤ <code>/pause</code> - Pause\n"
        f"➤ <code>/resume</code> - Resume\n"
        f"➤ <code>/skip</code> - Skip\n"
        f"➤ <code>/stop</code> - Stop & clear queue\n"
        f"➤ <code>/loop</code> - Toggle loop\n"
        f"➤ <code>/queue</code> - View queue\n"
        f"➤ <code>/ping</code> - Check status\n\n"
        f"<b>🛠️ Admin:</b> /ban, /unban, /mute, /unmute, /warn, /unwarn, /warns, /promote, /demote, /setwelcome, /delwelcome\n\n"
        f"<b>📢 Support:</b> @vanixsupport\n"
        f"<b>👨‍💻 Owner:</b> @vanixowner\n"
        f"<b>🧑‍💻 Creator:</b> @vanixcreator",
        parse_mode="html"
    )

# ============================================================
# 🔘 INLINE BUTTONS CALLBACK HANDLER
# ============================================================

@app.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    data = callback.data
    
    if data == "pause":
        try:
            await call.pause_stream(chat_id)
            await callback.answer("⏸ Paused", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "resume":
        try:
            await call.resume_stream(chat_id)
            await callback.answer("▶️ Resumed", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "skip":
        if current_track.get(chat_id):
            current_track[chat_id] = {}
            try:
                await call.stop_stream(chat_id)
            except:
                pass
            await play_next(chat_id)
            await callback.answer("⏭ Skipped", show_alert=True)
        else:
            await callback.answer("Nothing playing", show_alert=True)
    elif data == "loop":
        current = loop_status.get(chat_id, False)
        loop_status[chat_id] = not current
        await callback.answer(f"Loop: {'ON' if loop_status[chat_id] else 'OFF'}", show_alert=True)
    elif data == "stop":
        queues[chat_id] = []
        current_track[chat_id] = {}
        loop_status[chat_id] = False
        try:
            await call.leave_call(chat_id)
            await callback.answer("⏹ Stopped", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
        await callback.message.delete()
    elif data == "queue":
        if not queues.get(chat_id) and not current_track.get(chat_id):
            await callback.answer("Queue is empty", show_alert=True)
            return
        text = "✦ 𝗤𝗨𝗘𝗨𝗘 ✦\n\n"
        if current_track.get(chat_id):
            text += f"▶️ Now: {current_track[chat_id]['title']}\n"
        if queues.get(chat_id):
            text += "\nUp Next:\n"
            for i, song in enumerate(queues[chat_id][:10], 1):
                text += f"{i}. {song['title']}\n"
        await callback.answer(text[:200], show_alert=True)
    elif data == "vpause":
        try:
            await call.pause_stream(chat_id)
            await callback.answer("⏸ Video Paused", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "vresume":
        try:
            await call.resume_stream(chat_id)
            await callback.answer("▶️ Video Resumed", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    elif data == "vstop":
        try:
            await call.leave_call(chat_id)
            queues[chat_id] = []
            current_track[chat_id] = {}
            await callback.answer("⏹ Video Stream Stopped", show_alert=True)
            await callback.message.delete()
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)

# ============================================================
# 🚀 BOT LAUNCH
# ============================================================

async def main():
    print("""
    ✧･ﾟ: *✧･ﾟ:*  VΛПIΧ  MЦSIC  BӨƬ  *:･ﾟ✧*:･ﾟ✧
       ──── ⋆⋅☆⋅⋆ ──── ⋆⋅☆⋅⋆ ──── 
        ✦  P R E M I U M   E D I T I O N  ✦
       ──── ⋆⋅☆⋅⋆ ──── ⋆⋅☆⋅⋆ ────
    """)
    
    await app.start()
    await call.start()
    
    print(f"✅ Bot is running as {BOT_USERNAME}")
    print("📊 Commands: /play (Audio), /vplay (Video), /ban, /mute, /warn, /promote, /demote, /setwelcome")
    print("🤖 Press Ctrl+C to stop")
    
    await idle()

if __name__ == "__main__":
    asyncio.run(main())