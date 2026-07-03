"""
✧･ﾟ: *✧･ﾟ:*  VΛПIΧ MЦSIC BӨƬ  *:･ﾟ✧*:･ﾟ✧
         ⋆⋅☆⋅⋆  Premium Edition  ⋆⋅☆⋅⋆
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
from pytgcalls.types import MediaStream
from pytgcalls.exceptions import NoActiveGroupCall
import yt_dlp

# ============================================================
# ⚙️ CONFIGURATION - Environment Variables
# ============================================================

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("❌ ERROR: API_ID, API_HASH, BOT_TOKEN are required!")
    exit(1)

BOT_USERNAME = "@vanixmusic_bot"   # change to your bot's username

# ============================================================
# 🗄️ DATABASE SETUP
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
# 🚀 BOT & USER CLIENTS (separate)
# ============================================================

# Bot client (commands)
bot = Client(
    "vanix_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

# User client (voice chat)
if SESSION_STRING:
    user = Client(
        "vanix_user",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
    )
else:
    print("⚠️ WARNING: SESSION_STRING not set! Bot will not join VC.")
    user = None

# PyTgCalls client (needs user)
call = PyTgCalls(user) if user else None

# ============================================================
# 📊 GLOBAL STATE
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
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
    return await loop.run_in_executor(None, extract)

# ============================================================
# 🎶 PLAYBACK ENGINE (MediaStream)
# ============================================================

async def play_next(chat_id: int):
    if loop_status.get(chat_id, False) and chat_id in current_track and current_track[chat_id]:
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
        await call.play(chat_id, MediaStream(song['url']))
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Error: {e}")
        await play_next(chat_id)
        return
    
    await send_now_playing(chat_id, song)

async def send_now_playing(chat_id: int, song: dict):
    duration = song.get('duration_str', 'Unknown')
    text = (
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n"
        f"<b>   ⋆⋅☆⋅⋆  𝐍𝐎𝐖 𝐏𝐋𝐀𝐘𝐈𝐍𝐆  ⋆⋅☆⋅⋆</b>\n"
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n\n"
        f"<b>🎵 Title:</b> <a href='{song['webpage_url']}'>{song['title']}</a>\n"
        f"<b>⏱ Duration:</b> <code>{duration}</code>\n"
        f"<b>👤 Uploader:</b> {song.get('uploader', 'Unknown')}\n"
        f"<b>👀 Views:</b> {song.get('view_count', 0):,}\n\n"
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
    if song.get('thumbnail'):
        try:
            await bot.send_photo(chat_id, photo=song['thumbnail'], caption=text, reply_markup=keyboard, parse_mode="html")
        except Exception:
            await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)
    else:
        await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)

# ============================================================
# 🕵️ MANUAL STREAM MONITOR (Replaces on_stream_end decorator)
# ============================================================

async def stream_monitor():
    """Check every 2 seconds if a stream has ended and play next."""
    while True:
        await asyncio.sleep(2)
        if not call:
            continue
        
        # Create a copy of keys to avoid modification during iteration
        for chat_id in list(current_track.keys()):
            # If track is supposed to be playing, but call is not active
            if current_track.get(chat_id) and playing_status.get(chat_id, False):
                try:
                    # Check if the chat is still in a call
                    # If not in call, it means stream ended or stopped
                    # We will rely on a simple flag: if playing_status is True, 
                    # we assume it's playing. But we need to check actual status.
                    # Let's use the fact that if we try to get current stream and it fails,
                    # we play next.
                    await call.get_current_call(chat_id)
                except Exception:
                    # Not in call or stream ended
                    await play_next(chat_id)

# ============================================================
# 🛠️ ADMIN TOOLS
# ============================================================

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@bot.on_message(filters.command("ban") & filters.group)
async def ban_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to ban them.")
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ <b>Banned</b> user.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@bot.on_message(filters.command("unban") & filters.group)
async def unban_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    try:
        user_id = int(message.command[1]) if len(message.command) > 1 else None
        if not user_id:
            return await message.reply("❌ Usage: `/unban user_id`")
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.reply(f"✅ <b>Unbanned</b> User ID: `{user_id}`", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@bot.on_message(filters.command("mute") & filters.group)
async def mute_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user's message to mute them.")
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.restrict_chat_member(message.chat.id, user_id, ChatPermissions())
        await message.reply(f"🔇 <b>Muted</b> user.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@bot.on_message(filters.command("unmute") & filters.group)
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
        await bot.restrict_chat_member(message.chat.id, user_id, perms)
        await message.reply(f"🔊 <b>Unmuted</b> user.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@bot.on_message(filters.command("warn") & filters.group)
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
    await message.reply(f"⚠️ <b>Warning!</b> {target} ({count}/3)", parse_mode="html")
    if count >= 3:
        try:
            await bot.ban_chat_member(message.chat.id, user_id)
            await message.reply(f"🚫 {target} banned for 3 warnings!", parse_mode="html")
            warnings[chat_id][str(user_id)] = 0
            update_db()
        except Exception as e:
            await message.reply(f"❌ Auto-ban failed: {e}")

@bot.on_message(filters.command("unwarn") & filters.group)
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
        update_db()
        await message.reply(f"✅ Removed 1 warning from {target}.", parse_mode="html")
    else:
        await message.reply(f"ℹ️ {target} has no warnings.", parse_mode="html")

@bot.on_message(filters.command("warns") & filters.group)
async def warns_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if not message.reply_to_message:
        user_id = str(message.from_user.id)
        count = warnings.get(chat_id, {}).get(user_id, 0)
        await message.reply(f"📊 <b>Your Warnings:</b> `{count}`", parse_mode="html")
    else:
        if not await is_admin(message.chat.id, message.from_user.id):
            return await message.reply("❌ Only admins can check others.")
        user_id = str(message.reply_to_message.from_user.id)
        target = message.reply_to_message.from_user.mention
        count = warnings.get(chat_id, {}).get(user_id, 0)
        await message.reply(f"📊 <b>{target}:</b> `{count}` warnings", parse_mode="html")

@bot.on_message(filters.command("setwelcome") & filters.group)
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
            return await message.reply("❌ Reply to a text message.")
    else:
        if len(message.command) < 2:
            return await message.reply("❌ Usage: `/setwelcome Welcome!`")
        welcome_msgs[chat_id] = " ".join(message.command[1:])
    update_db()
    await message.reply(f"✅ Welcome set.", parse_mode="html")

@bot.on_message(filters.command("delwelcome") & filters.group)
async def delwelcome_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    chat_id = str(message.chat.id)
    if chat_id in welcome_msgs:
        del welcome_msgs[chat_id]
        update_db()
        await message.reply("✅ Welcome deleted.", parse_mode="html")
    else:
        await message.reply("ℹ️ No welcome set.", parse_mode="html")

@bot.on_message(filters.command("promote") & filters.group)
async def promote_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user.")
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    try:
        await bot.promote_chat_member(
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
        await message.reply(f"✅ <b>Promoted</b> {target} (without ban/promote rights).", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@bot.on_message(filters.command("demote") & filters.group)
async def demote_command(client: Client, message: Message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not an admin!")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user.")
    user_id = message.reply_to_message.from_user.id
    target = message.reply_to_message.from_user.mention
    try:
        await bot.promote_chat_member(
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
        await message.reply(f"✅ <b>Demoted</b> {target}.", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@bot.on_message(filters.group & filters.new_chat_members)
async def welcome_new_member(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if chat_id in welcome_msgs:
        for member in message.new_chat_members:
            if member.id == (await bot.get_me()).id:
                continue
            welcome_text = welcome_msgs[chat_id]
            welcome_text = welcome_text.replace("{name}", member.mention)
            welcome_text = welcome_text.replace("{username}", f"@{member.username}" if member.username else "No Username")
            await message.reply(welcome_text, parse_mode="html")
            break

# ============================================================
# 🎮 MUSIC COMMANDS
# ============================================================

@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    intro_text = (
        "<b>✧･ﾟ: *✧･ﾟ:*  𝐕𝐀𝐍𝐈𝐗 𝐌𝐔𝐒𝐈𝐂  *:･ﾟ✧*:･ﾟ✧</b>\n"
        "<b>     ⋆⋅☆⋅⋆  Premium Edition  ⋆⋅☆⋅⋆</b>\n\n"
        "<b>✦ Telegram's smoothest bot for VC audio & video playback</b>\n\n"
        "<b>🎧 Features</b>\n"
        "➤ <b>HD Audio</b> - Crystal-clear sound\n"
        "➤ <b>HD Video</b> - Perfect playback\n"
        "➤ <b>Admin Tools</b> - Ban, Mute, Warn, Promote\n"
        "➤ <b>Zero-Lag Core</b> - Feels fast & easy\n\n"
        "<b>🚀 Quick Commands</b>\n"
        "➤ <code>/play &lt;song&gt;</code> - Play audio\n"
        "➤ <code>/vplay &lt;song&gt;</code> - Stream video\n"
        "➤ <code>/pause | /resume | /skip | /stop | /loop | /queue</code>\n\n"
        "<b>🛠️ Admin</b>\n"
        "➤ <code>/ban | /unban | /mute | /unmute</code>\n"
        "➤ <code>/warn | /unwarn | /warns</code>\n"
        "➤ <code>/promote | /demote</code>\n"
        "➤ <code>/setwelcome | /delwelcome</code>\n\n"
        "<b>📢 Add me to your group and enjoy!</b>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Add to Group", url="https://t.me/vanixmusic_bot?startgroup=true")],
        [
            InlineKeyboardButton("💬 Support", url="https://t.me/vanixsupport"),
            InlineKeyboardButton("👨‍💻 Owner", url="https://t.me/vanixowner"),
            InlineKeyboardButton("🧑‍💻 Creator", url="https://t.me/vanixcreator"),
        ]
    ])
    await message.reply(intro_text, parse_mode="html", disable_web_page_preview=True, reply_markup=keyboard)

@bot.on_message(filters.command(["play", "p"]))
async def play_command(client: Client, message: Message):
    if not user or not call:
        return await message.reply("❌ SESSION_STRING not set. Can't play music.")
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/play song name`", parse_mode="html")
        return
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 Searching...", parse_mode="html")
    try:
        song_info = await get_audio_info(query)
    except Exception as e:
        await msg.edit(f"❌ Error: {e}", parse_mode="html")
        return
    if chat_id not in queues:
        queues[chat_id] = []
    if not current_track.get(chat_id) or not playing_status.get(chat_id, False):
        queues[chat_id].append(song_info)
        await msg.edit(f"▶️ Now playing: {song_info['title']}", parse_mode="html")
        await play_next(chat_id)
    else:
        position = len(queues[chat_id]) + 1
        queues[chat_id].append(song_info)
        await msg.edit(f"✅ Added to queue at position {position}", parse_mode="html")

@bot.on_message(filters.command(["vplay", "vp"]))
async def vplay_command(client: Client, message: Message):
    if not user or not call:
        return await message.reply("❌ SESSION_STRING not set. Can't play video.")
    if len(message.command) < 2:
        await message.reply("❌ Usage: `/vplay video name`", parse_mode="html")
        return
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 Searching video...", parse_mode="html")
    try:
        video_info = await get_video_info(query)
    except Exception as e:
        await msg.edit(f"❌ Error: {e}", parse_mode="html")
        return
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    try:
        await call.leave_call(chat_id)
    except:
        pass
    try:
        await call.join_call(chat_id)
        await call.play(chat_id, MediaStream(video_info['url']))
        current_track[chat_id] = video_info
        playing_status[chat_id] = True
        await msg.edit(f"📺 Now streaming: {video_info['title']}\n\nMake sure Video Call is active!", parse_mode="html")
    except Exception as e:
        await msg.edit(f"❌ Error: {e}\n\nStart a Video Call first!", parse_mode="html")

@bot.on_message(filters.command("pause"))
async def pause_command(client: Client, message: Message):
    if not call:
        return
    chat_id = message.chat.id
    try:
        await call.pause_stream(chat_id)
        await message.reply("⏸ Paused", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ {e}", parse_mode="html")

@bot.on_message(filters.command("resume"))
async def resume_command(client: Client, message: Message):
    if not call:
        return
    chat_id = message.chat.id
    try:
        await call.resume_stream(chat_id)
        await message.reply("▶️ Resumed", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ {e}", parse_mode="html")

@bot.on_message(filters.command(["skip", "next"]))
async def skip_command(client: Client, message: Message):
    if not call:
        return
    chat_id = message.chat.id
    if not current_track.get(chat_id):
        await message.reply("❌ Nothing playing.", parse_mode="html")
        return
    try:
        await call.stop_stream(chat_id)
    except:
        pass
    await play_next(chat_id)
    await message.reply("⏭ Skipped", parse_mode="html")

@bot.on_message(filters.command(["stop", "end"]))
async def stop_command(client: Client, message: Message):
    if not call:
        return
    chat_id = message.chat.id
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    try:
        await call.leave_call(chat_id)
        await message.reply("⏹ Stopped and left VC", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ {e}", parse_mode="html")

@bot.on_message(filters.command("loop"))
async def loop_command(client: Client, message: Message):
    chat_id = message.chat.id
    current = loop_status.get(chat_id, False)
    loop_status[chat_id] = not current
    status = "ON 🔁" if loop_status[chat_id] else "OFF ➡️"
    await message.reply(f"🔄 Loop: {status}", parse_mode="html")

@bot.on_message(filters.command(["queue", "q"]))
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not queues.get(chat_id) and not current_track.get(chat_id):
        await message.reply("📭 Queue is empty", parse_mode="html")
        return
    text = "<b>✦ QUEUE ✦</b>\n\n"
    if current_track.get(chat_id):
        text += f"▶️ Now: {current_track[chat_id]['title']}\n\n"
    if queues.get(chat_id):
        for i, song in enumerate(queues[chat_id][:15], 1):
            text += f"{i}. {song['title']}\n"
        if len(queues[chat_id]) > 15:
            text += f"\n... and {len(queues[chat_id])-15} more"
    await message.reply(text, parse_mode="html")

@bot.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = datetime.now()
    msg = await message.reply("🏓 Pinging...", parse_mode="html")
    end = datetime.now()
    latency = (end - start).microseconds / 1000
    await msg.edit(f"🏓 Pong!\n⚡ Latency: {latency:.2f}ms", parse_mode="html")

@bot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply(
        f"<b>🎯 Commands</b>\n"
        f"/play <song> - Play audio\n"
        f"/vplay <song> - Stream video\n"
        f"/pause | /resume | /skip | /stop | /loop | /queue\n\n"
        f"<b>🛠️ Admin</b>\n"
        f"/ban | /unban | /mute | /unmute\n"
        f"/warn | /unwarn | /warns\n"
        f"/promote | /demote\n"
        f"/setwelcome | /delwelcome",
        parse_mode="html"
    )

# ============================================================
# 🔘 CALLBACK HANDLER
# ============================================================

@bot.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    if not call:
        return await callback.answer("Voice client not ready", show_alert=True)
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
        text = "Queue:\n"
        if current_track.get(chat_id):
            text += f"▶️ Now: {current_track[chat_id]['title']}\n"
        if queues.get(chat_id):
            for i, song in enumerate(queues[chat_id][:5], 1):
                text += f"{i}. {song['title']}\n"
            if len(queues[chat_id]) > 5:
                text += f"... and {len(queues[chat_id])-5} more"
        await callback.answer(text, show_alert=True)

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
    await bot.start()
    print(f"✅ Bot client started as {BOT_USERNAME}")

    if user:
        await user.start()
        print("✅ User client started (String Session).")
    else:
        print("⚠️ User client not started (missing SESSION_STRING). Voice commands will fail.")

    if call:
        await call.start()
        print("✅ PyTgCalls client started.")
        # Start the manual stream monitor
        asyncio.create_task(stream_monitor())
        print("🔄 Stream monitor started.")
    else:
        print("⚠️ PyTgCalls not started (no user client).")

    print("📊 Bot is running! Commands: /play, /vplay, /ban, /mute, /warn, /promote, /setwelcome")
    await idle()

    await bot.stop()
    if user:
        await user.stop()

if __name__ == "__main__":
    asyncio.run(main())
