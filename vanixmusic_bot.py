"""
✨✨✨ VΛNIX MUSIC - GOD EDITION ✨✨✨
(Fixed: Bot runs even if Session fails, Added Inline Buttons, Fixed VC errors)
"""

import os
import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List

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
# ⚙️ CONFIG
# ============================================================

API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")
BOT_USERNAME = "@vanixmusic_bot"  # अपना बॉट यूजरनेम लिखें

if not API_ID or not API_HASH or not BOT_TOKEN:
    print("❌ ERROR: API_ID, API_HASH, BOT_TOKEN required!")
    exit(1)

# ============================================================
# 📂 DATA
# ============================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"warnings": {}, "welcome": {}, "goodbye": {}, "playlists": {}, "saved": {}, "settings": {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

db = load_data()

def get_group_settings(chat_id: str) -> dict:
    if chat_id not in db.get("settings", {}):
        db["settings"][chat_id] = {"welcome": None, "goodbye": None, "warn_limit": 3, "warn_action": "mute"}
        save_data(db)
    return db["settings"][chat_id]

def update_group_settings(chat_id: str, **kwargs):
    if "settings" not in db:
        db["settings"] = {}
    if chat_id not in db["settings"]:
        db["settings"][chat_id] = {}
    for key, val in kwargs.items():
        db["settings"][chat_id][key] = val
    save_data(db)

# ============================================================
# 🤖 CLIENTS
# ============================================================

bot = Client("vanix_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("vanix_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING) if SESSION_STRING else None
call = None  # Will be initialized only if user starts

# ============================================================
# 📊 STATE
# ============================================================

queues: Dict[int, List[dict]] = {}
current_track: Dict[int, dict] = {}
loop_status: Dict[int, bool] = {}
playing_status: Dict[int, bool] = {}
volume_status: Dict[int, int] = {}

# ============================================================
# 🎵 YT-DLP
# ============================================================

async def get_audio_info(query: str) -> dict:
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True, 'default_search': 'ytsearch'}
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            dur = info.get('duration', 0)
            dur_str = f"{dur//60:02d}:{dur%60:02d}" if dur else "🔴 Live"
            return {
                'title': info.get('title', 'Unknown'),
                'duration': dur,
                'duration_str': dur_str,
                'url': info['url'],
                'webpage_url': info.get('webpage_url', ''),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
    return await loop.run_in_executor(None, extract)

async def get_video_info(query: str) -> dict:
    ydl_opts = {'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best', 'quiet': True, 'no_warnings': True, 'default_search': 'ytsearch'}
    loop = asyncio.get_event_loop()
    def extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            dur = info.get('duration', 0)
            dur_str = f"{dur//60:02d}:{dur%60:02d}" if dur else "🔴 Live"
            return {
                'title': info.get('title', 'Unknown'),
                'duration': dur,
                'duration_str': dur_str,
                'url': info['url'],
                'webpage_url': info.get('webpage_url', ''),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
    return await loop.run_in_executor(None, extract)

# ============================================================
# 🎶 PLAYBACK
# ============================================================

def get_progress_bar(current_sec: int, total_sec: int, length: int = 16) -> str:
    if total_sec == 0:
        return "🔴 Live"
    percent = current_sec / total_sec
    filled = int(round(length * percent))
    empty = length - filled
    return "█" * filled + "▬" * empty

async def play_next(chat_id: int):
    if loop_status.get(chat_id, False) and current_track.get(chat_id):
        queues[chat_id].insert(0, current_track[chat_id])
    
    if not queues.get(chat_id):
        try:
            await call.leave_call(chat_id)
        except: pass
        current_track[chat_id] = {}
        playing_status[chat_id] = False
        return
    
    song = queues[chat_id].pop(0)
    current_track[chat_id] = song
    playing_status[chat_id] = True
    try:
        await call.join_call(chat_id)
        await call.play(chat_id, MediaStream(song['url']))
        if chat_id in volume_status:
            await call.set_volume(chat_id, volume_status[chat_id])
    except NoActiveGroupCall:
        await bot.send_message(chat_id, "❌ No active voice chat found! Please start a voice chat first.")
        await play_next(chat_id)
        return
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Error: {e}")
        await play_next(chat_id)
        return
    await send_now_playing(chat_id, song)

async def send_now_playing(chat_id: int, song: dict):
    dur = song.get('duration', 0)
    dur_str = song.get('duration_str', '🔴 Live')
    vol = volume_status.get(chat_id, 100)
    q_len = len(queues.get(chat_id, []))
    bar = get_progress_bar(0, dur, 16) if dur else "🔴 Live"
    
    text = (
        f"<b>✨ 𝐍𝐎𝐖 𝐏𝐋𝐀𝐘𝐈𝐍𝐆 ✨</b>\n"
        f"<b>▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔</b>\n\n"
        f"<b>🎵 {song['title']}</b>\n"
        f"<b>⏱ {dur_str}</b>\n"
        f"<b>{bar}</b>\n"
        f"<b>👤 {song.get('uploader', 'Unknown')}</b>  •  <b>👀 {song.get('view_count', 0):,}</b>\n"
        f"<b>🔊 {vol}%</b>  •  <b>📊 {q_len}</b> Songs remaining\n"
        f"<b>▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔</b>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data="pause"),
            InlineKeyboardButton("▶️ Resume", callback_data="resume"),
            InlineKeyboardButton("⏭ Skip", callback_data="skip"),
            InlineKeyboardButton("⏹ Stop", callback_data="stop"),
        ],
        [
            InlineKeyboardButton("🔁 Loop", callback_data="loop"),
            InlineKeyboardButton("🔀 Shuffle", callback_data="shuffle"),
            InlineKeyboardButton("📋 Queue", callback_data="queue"),
        ],
        [
            InlineKeyboardButton("🔉 -10s", callback_data="seek_back"),
            InlineKeyboardButton("🔊 +10s", callback_data="seek_forward"),
        ],
        [
            InlineKeyboardButton("🔉 Vol -", callback_data="vol_down"),
            InlineKeyboardButton("🔊 Vol +", callback_data="vol_up"),
        ],
        [
            InlineKeyboardButton("💾 Save", callback_data="save_track"),
            InlineKeyboardButton("📀 Add Playlist", callback_data="add_playlist"),
        ]
    ])
    
    try:
        if song.get('thumbnail'):
            await bot.send_photo(chat_id, photo=song['thumbnail'], caption=text, reply_markup=keyboard, parse_mode="html")
        else:
            await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)
    except Exception:
        await bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)

# ============================================================
# 🕵️ MONITOR
# ============================================================

async def stream_monitor():
    while True:
        await asyncio.sleep(3)
        if not call:
            continue
        for chat_id in list(current_track.keys()):
            if current_track.get(chat_id) and playing_status.get(chat_id, False):
                try:
                    await call.get_current_call(chat_id)
                except NoActiveGroupCall:
                    await play_next(chat_id)
                except Exception:
                    await play_next(chat_id)
                    break

# ============================================================
# 🛠️ ADMIN CHECK
# ============================================================

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# ============================================================
# 🎮 MUSIC COMMANDS
# ============================================================

@bot.on_message(filters.command(["play", "p"]))
async def play_command(client: Client, message: Message):
    if not call:
        return await message.reply("❌ SESSION_STRING invalid or VC not initialized.")
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/play song`")
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 Searching...")
    try:
        song = await get_audio_info(query)
    except Exception as e:
        return await msg.edit(f"❌ {e}")
    if chat_id not in queues:
        queues[chat_id] = []
    if not current_track.get(chat_id) or not playing_status.get(chat_id, False):
        queues[chat_id].append(song)
        await msg.edit(f"▶️ Now: {song['title']}")
        await play_next(chat_id)
    else:
        pos = len(queues[chat_id]) + 1
        queues[chat_id].append(song)
        await msg.edit(f"✅ Added Queue (#{pos}): {song['title']}")

@bot.on_message(filters.command(["vplay", "vp"]))
async def vplay_command(client: Client, message: Message):
    if not call:
        return await message.reply("❌ SESSION_STRING invalid or VC not initialized.")
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/vplay video`")
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    msg = await message.reply("🔍 Searching Video...")
    try:
        song = await get_video_info(query)
    except Exception as e:
        return await msg.edit(f"❌ {e}")
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    try:
        await call.leave_call(chat_id)
    except: pass
    try:
        await call.join_call(chat_id)
        await call.play(chat_id, MediaStream(song['url']))
        current_track[chat_id] = song
        playing_status[chat_id] = True
        await msg.edit(f"📺 Now Streaming: {song['title']}")
    except NoActiveGroupCall:
        await msg.edit("❌ No active voice chat found! Please start a voice chat first.")
    except Exception as e:
        await msg.edit(f"❌ {e}\n\nStart a Video Call first!")

@bot.on_message(filters.command(["pause", "resume", "skip", "stop", "loop", "shuffle"]))
async def control_commands(client: Client, message: Message):
    if not call:
        return await message.reply("❌ VC not ready.")
    chat_id = message.chat.id
    cmd = message.command[0].lower()
    if cmd == "pause":
        try:
            await call.pause_stream(chat_id)
            await message.reply("⏸ Paused")
        except Exception as e:
            await message.reply(f"❌ {e}")
    elif cmd == "resume":
        try:
            await call.resume_stream(chat_id)
            await message.reply("▶️ Resumed")
        except Exception as e:
            await message.reply(f"❌ {e}")
    elif cmd == "skip":
        if not current_track.get(chat_id):
            return await message.reply("❌ Nothing playing.")
        await message.reply("⏭ Skipped")
        try:
            await call.stop_stream(chat_id)
        except: pass
        await play_next(chat_id)
    elif cmd == "stop":
        queues[chat_id] = []
        current_track[chat_id] = {}
        loop_status[chat_id] = False
        try:
            await call.leave_call(chat_id)
            await message.reply("⏹ Stopped")
        except Exception as e:
            await message.reply(f"❌ {e}")
    elif cmd == "loop":
        loop_status[chat_id] = not loop_status.get(chat_id, False)
        await message.reply(f"🔄 Loop: {'ON' if loop_status[chat_id] else 'OFF'}")
    elif cmd == "shuffle":
        if not queues.get(chat_id) or len(queues[chat_id]) < 2:
            return await message.reply("❌ Need 2+ songs in queue.")
        random.shuffle(queues[chat_id])
        await message.reply("🔀 Queue Shuffled!")

@bot.on_message(filters.command(["queue", "q"]))
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not queues.get(chat_id) and not current_track.get(chat_id):
        return await message.reply("📭 Queue empty.")
    text = "<b>📋 QUEUE</b>\n\n"
    if current_track.get(chat_id):
        text += f"▶️ Now: {current_track[chat_id]['title']}\n\n"
    for i, s in enumerate(queues.get(chat_id, [])[:15], 1):
        text += f"{i}. {s['title']}\n"
    await message.reply(text, parse_mode="html")

@bot.on_message(filters.command(["volume", "vol"]))
async def volume_command(client: Client, message: Message):
    if not call:
        return
    if len(message.command) < 2:
        return await message.reply("Usage: `/volume 0-200`")
    try:
        vol = int(message.command[1])
        if vol < 0 or vol > 200:
            return await message.reply("❌ 0 to 200 only.")
        chat_id = message.chat.id
        volume_status[chat_id] = vol
        await call.set_volume(chat_id, vol)
        await message.reply(f"🔊 Volume: {vol}%")
    except:
        await message.reply("❌ Invalid number.")

@bot.on_message(filters.command(["seek"]))
async def seek_command(client: Client, message: Message):
    if not call:
        return
    if len(message.command) < 2:
        return await message.reply("Usage: `/seek seconds`")
    try:
        seconds = int(message.command[1])
        chat_id = message.chat.id
        if not current_track.get(chat_id):
            return await message.reply("❌ Nothing playing.")
        song = current_track[chat_id]
        await call.stop_stream(chat_id)
        await call.play(chat_id, MediaStream(f"{song['url']}#t={seconds}"))
        await message.reply(f"⏩ Seeked to {seconds}s")
    except:
        await message.reply("❌ Seek failed.")

# ============================================================
# 📀 PLAYLIST & SAVE
# ============================================================

@bot.on_message(filters.command("playlist"))
async def playlist_command(client: Client, message: Message):
    user_id = str(message.from_user.id)
    if "playlists" not in db:
        db["playlists"] = {}
    if user_id not in db["playlists"]:
        db["playlists"][user_id] = []
    songs = db["playlists"][user_id]
    
    if len(message.command) < 2:
        return await message.reply(
            "📀 **Playlist Commands**\n"
            "`/playlist add <song>`\n"
            "`/playlist list`\n"
            "`/playlist remove <index>`\n"
            "`/playlist clear`",
            parse_mode="html"
        )
    action = message.command[1].lower()
    
    if action == "add":
        if len(message.command) < 3:
            return await message.reply("❌ Usage: `/playlist add <song>`")
        query = " ".join(message.command[2:])
        msg = await message.reply("🔍 Searching...")
        try:
            song = await get_audio_info(query)
        except Exception as e:
            return await msg.edit(f"❌ {e}")
        songs.append(song)
        save_data(db)
        await msg.edit(f"✅ Added to Playlist: {song['title']}")
    
    elif action == "list":
        if not songs:
            return await message.reply("📭 Playlist empty.")
        text = "📀 **Your Playlist**\n\n"
        for i, s in enumerate(songs[:30], 1):
            text += f"{i}. {s['title']} ({s['duration_str']})\n"
        await message.reply(text, parse_mode="html")
    
    elif action == "remove":
        if len(message.command) < 3:
            return await message.reply("❌ Usage: `/playlist remove <index>`")
        try:
            idx = int(message.command[2]) - 1
            if idx < 0 or idx >= len(songs):
                return await message.reply("❌ Invalid index.")
            removed = songs.pop(idx)
            save_data(db)
            await message.reply(f"✅ Removed: {removed['title']}")
        except:
            await message.reply("❌ Invalid index.")
    
    elif action == "clear":
        db["playlists"][user_id] = []
        save_data(db)
        await message.reply("🗑️ Playlist cleared.")

@bot.on_message(filters.command(["save", "saved"]))
async def save_commands(client: Client, message: Message):
    user_id = str(message.from_user.id)
    if "saved" not in db:
        db["saved"] = {}
    if user_id not in db["saved"]:
        db["saved"][user_id] = []
    saved = db["saved"][user_id]
    cmd = message.command[0].lower()
    
    if cmd == "save":
        chat_id = message.chat.id
        if not current_track.get(chat_id):
            return await message.reply("❌ Nothing playing.")
        song = current_track[chat_id]
        for s in saved:
            if s['title'] == song['title']:
                return await message.reply("ℹ️ Already saved.")
        saved.append(song)
        save_data(db)
        await message.reply(f"💾 Saved: {song['title']}")
    else:
        if not saved:
            return await message.reply("📭 No saved tracks.")
        text = "📚 **Saved Tracks**\n\n"
        for i, s in enumerate(saved[:30], 1):
            text += f"{i}. {s['title']} ({s['duration_str']})\n"
        await message.reply(text, parse_mode="html")

@bot.on_message(filters.command("remove"))
async def remove_queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not queues.get(chat_id):
        return await message.reply("❌ Queue empty.")
    if len(message.command) < 2:
        return await message.reply("Usage: `/remove <index>`")
    try:
        idx = int(message.command[1]) - 1
        if idx < 0 or idx >= len(queues[chat_id]):
            return await message.reply("❌ Invalid index.")
        removed = queues[chat_id].pop(idx)
        await message.reply(f"🗑️ Removed: {removed['title']}")
    except:
        await message.reply("❌ Invalid.")

# ============================================================
# 🛡️ ADMIN
# ============================================================

@bot.on_message(filters.command(["ban", "unban", "mute", "unmute", "kick", "promote", "demote"]))
async def admin_actions(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user.")
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply("❌ You are not admin.")
    
    chat_id = message.chat.id
    target = message.reply_to_message.from_user
    cmd = message.command[0].lower()
    reason = " ".join(message.command[1:]) or "No reason"
    
    try:
        if cmd == "ban":
            await bot.ban_chat_member(chat_id, target.id)
            await message.reply(f"🚫 Banned {target.mention}.\nReason: {reason}")
        elif cmd == "unban":
            await bot.unban_chat_member(chat_id, target.id)
            await message.reply(f"✅ Unbanned {target.mention}.")
        elif cmd == "kick":
            await bot.ban_chat_member(chat_id, target.id)
            await bot.unban_chat_member(chat_id, target.id)
            await message.reply(f"👢 Kicked {target.mention}.\nReason: {reason}")
        elif cmd == "mute":
            await bot.restrict_chat_member(chat_id, target.id, ChatPermissions())
            await message.reply(f"🔇 Muted {target.mention}.\nReason: {reason}")
        elif cmd == "unmute":
            perms = ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True)
            await bot.restrict_chat_member(chat_id, target.id, perms)
            await message.reply(f"🔊 Unmuted {target.mention}.")
        elif cmd == "promote":
            await bot.promote_chat_member(chat_id, target.id, can_manage_chat=True, can_change_info=True, can_delete_messages=True, can_invite_users=True, can_pin_messages=True)
            await message.reply(f"✅ Promoted {target.mention}.")
        elif cmd == "demote":
            await bot.promote_chat_member(chat_id, target.id, can_manage_chat=False, can_change_info=False, can_delete_messages=False, can_invite_users=False, can_pin_messages=False)
            await message.reply(f"✅ Demoted {target.mention}.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@bot.on_message(filters.command(["warn", "unwarn", "warns"]))
async def warn_commands(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if "warnings" not in db:
        db["warnings"] = {}
    if chat_id not in db["warnings"]:
        db["warnings"][chat_id] = {}
    
    cmd = message.command[0].lower()
    target = message.reply_to_message.from_user if message.reply_to_message else None
    target_id = str(target.id) if target else str(message.from_user.id)
    
    if cmd == "warns":
        if target and not await is_admin(int(chat_id), message.from_user.id):
            return await message.reply("❌ Only admins can check others.")
        count = db["warnings"][chat_id].get(target_id, 0)
        await message.reply(f"📊 Warnings: {count}")
        return
    
    if not await is_admin(int(chat_id), message.from_user.id):
        return await message.reply("❌ You are not admin.")
    if not message.reply_to_message:
        return await message.reply("❌ Reply to a user.")
    
    reason = " ".join(message.command[1:]) or "No reason"
    settings = get_group_settings(chat_id)
    limit = settings.get("warn_limit", 3)
    
    if cmd == "warn":
        db["warnings"][chat_id][target_id] = db["warnings"][chat_id].get(target_id, 0) + 1
        count = db["warnings"][chat_id][target_id]
        save_data(db)
        await message.reply(f"⚠️ Warned {target.mention} ({count}/{limit})\nReason: {reason}")
        if count >= limit:
            action = settings.get("warn_action", "mute")
            try:
                if action == "mute":
                    await bot.restrict_chat_member(int(chat_id), target.id, ChatPermissions())
                elif action == "kick":
                    await bot.ban_chat_member(int(chat_id), target.id)
                    await bot.unban_chat_member(int(chat_id), target.id)
                elif action == "ban":
                    await bot.ban_chat_member(int(chat_id), target.id)
                await message.reply(f"🚨 Auto-{action} for {target.mention} (Warn limit reached).")
                db["warnings"][chat_id][target_id] = 0
                save_data(db)
            except Exception as e:
                await message.reply(f"❌ Auto-action failed: {e}")
    
    elif cmd == "unwarn":
        if db["warnings"][chat_id].get(target_id, 0) > 0:
            db["warnings"][chat_id][target_id] -= 1
            save_data(db)
            await message.reply(f"✅ Removed 1 warning from {target.mention}.")
        else:
            await message.reply(f"ℹ️ No warnings for {target.mention}.")

# ============================================================
# 💬 WELCOME / GOODBYE
# ============================================================

@bot.on_message(filters.command(["setwelcome", "delwelcome", "setgoodbye", "delgoodbye"]))
async def welcome_goodbye(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if not await is_admin(int(chat_id), message.from_user.id):
        return await message.reply("❌ You are not admin.")
    
    if "welcome" not in db:
        db["welcome"] = {}
    if "goodbye" not in db:
        db["goodbye"] = {}
    
    cmd = message.command[0].lower()
    if cmd == "setwelcome":
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        elif len(message.command) > 1:
            text = " ".join(message.command[1:])
        else:
            return await message.reply("❌ Usage: `/setwelcome Welcome!`")
        db["welcome"][chat_id] = text
        save_data(db)
        await message.reply("✅ Welcome set.")
    elif cmd == "delwelcome":
        if chat_id in db["welcome"]:
            del db["welcome"][chat_id]
            save_data(db)
        await message.reply("✅ Welcome deleted.")
    elif cmd == "setgoodbye":
        if message.reply_to_message and message.reply_to_message.text:
            text = message.reply_to_message.text
        elif len(message.command) > 1:
            text = " ".join(message.command[1:])
        else:
            return await message.reply("❌ Usage: `/setgoodbye Bye!`")
        db["goodbye"][chat_id] = text
        save_data(db)
        await message.reply("✅ Goodbye set.")
    elif cmd == "delgoodbye":
        if chat_id in db["goodbye"]:
            del db["goodbye"][chat_id]
            save_data(db)
        await message.reply("✅ Goodbye deleted.")

@bot.on_message(filters.group & filters.new_chat_members)
async def on_welcome(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if chat_id not in db.get("welcome", {}):
        return
    for member in message.new_chat_members:
        if member.id == (await bot.get_me()).id:
            continue
        text = db["welcome"][chat_id].replace("{name}", member.mention).replace("{title}", message.chat.title)
        await message.reply(text, parse_mode="html")

@bot.on_message(filters.group & filters.left_chat_member)
async def on_goodbye(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if chat_id not in db.get("goodbye", {}):
        return
    member = message.left_chat_member
    text = db["goodbye"][chat_id].replace("{name}", member.mention)
    await message.reply(text, parse_mode="html")

# ============================================================
# ⚙️ SETTINGS
# ============================================================

@bot.on_message(filters.command("settings"))
async def settings_command(client: Client, message: Message):
    chat_id = str(message.chat.id)
    if not await is_admin(int(chat_id), message.from_user.id):
        return await message.reply("❌ You are not admin.")
    settings = get_group_settings(chat_id)
    text = (
        f"<b>⚙️ {message.chat.title} SETTINGS</b>\n\n"
        f"<b>Welcome:</b> {'✅' if settings.get('welcome') else '❌'}\n"
        f"<b>Goodbye:</b> {'✅' if settings.get('goodbye') else '❌'}\n"
        f"<b>Warn Limit:</b> {settings.get('warn_limit', 3)}\n"
        f"<b>Warn Action:</b> {settings.get('warn_action', 'mute')}\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Toggle Welcome", callback_data="settings_welcome")],
        [InlineKeyboardButton("🔄 Toggle Goodbye", callback_data="settings_goodbye")],
        [InlineKeyboardButton("⚠️ Set Warn Action", callback_data="settings_warnaction")],
    ])
    await message.reply(text, reply_markup=keyboard, parse_mode="html")

# ============================================================
# 🔘 CALLBACK
# ============================================================

@bot.on_callback_query()
async def callback_handler(client: Client, callback: CallbackQuery):
    if not call:
        return await callback.answer("VC not ready", True)
    
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    data = callback.data
    await callback.answer()
    
    if data.startswith("settings_"):
        action = data.split("_")[1]
        settings = get_group_settings(str(chat_id))
        if action == "welcome":
            current = settings.get("welcome")
            update_group_settings(str(chat_id), welcome=not current if isinstance(current, bool) else False)
            await callback.message.edit_text("✅ Toggled Welcome.")
        elif action == "goodbye":
            current = settings.get("goodbye")
            update_group_settings(str(chat_id), goodbye=not current if isinstance(current, bool) else False)
            await callback.message.edit_text("✅ Toggled Goodbye.")
        elif action == "warnaction":
            keyboard = [
                [InlineKeyboardButton("Mute", callback_data="set_warn_mute")],
                [InlineKeyboardButton("Kick", callback_data="set_warn_kick")],
                [InlineKeyboardButton("Ban", callback_data="set_warn_ban")]
            ]
            await callback.message.edit_text("Select Warn Action:", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    if data.startswith("set_warn_"):
        action = data.split("_")[2]
        update_group_settings(str(chat_id), warn_action=action)
        await callback.message.edit_text(f"✅ Warn Action set to {action.capitalize()}")
        return
    
    if data == "pause":
        try:
            await call.pause_stream(chat_id)
            await callback.answer("⏸ Paused", True)
        except Exception as e:
            await callback.answer(f"Error: {e}", True)
    elif data == "resume":
        try:
            await call.resume_stream(chat_id)
            await callback.answer("▶️ Resumed", True)
        except Exception as e:
            await callback.answer(f"Error: {e}", True)
    elif data == "skip":
        if current_track.get(chat_id):
            await callback.answer("⏭ Skipped", True)
            try:
                await call.stop_stream(chat_id)
            except: pass
            await play_next(chat_id)
        else:
            await callback.answer("Nothing playing", True)
    elif data == "stop":
        queues[chat_id] = []
        current_track[chat_id] = {}
        loop_status[chat_id] = False
        try:
            await call.leave_call(chat_id)
            await callback.answer("⏹ Stopped", True)
        except Exception as e:
            await callback.answer(f"Error: {e}", True)
        await callback.message.delete()
    elif data == "loop":
        loop_status[chat_id] = not loop_status.get(chat_id, False)
        await callback.answer(f"Loop: {'ON' if loop_status[chat_id] else 'OFF'}", True)
    elif data == "shuffle":
        if queues.get(chat_id) and len(queues[chat_id]) > 1:
            random.shuffle(queues[chat_id])
            await callback.answer("🔀 Shuffled!", True)
        else:
            await callback.answer("Need 2+ songs", True)
    elif data == "queue":
        q = queues.get(chat_id, [])
        cur = current_track.get(chat_id)
        if not cur and not q:
            return await callback.answer("Queue empty", True)
        text = f"Now: {cur['title']}\n" if cur else ""
        for i, s in enumerate(q[:5], 1):
            text += f"{i}. {s['title']}\n"
        await callback.answer(text, True)
    elif data == "vol_up":
        vol = volume_status.get(chat_id, 100) + 10
        if vol > 200:
            vol = 200
        volume_status[chat_id] = vol
        await call.set_volume(chat_id, vol)
        await callback.answer(f"🔊 {vol}%", True)
    elif data == "vol_down":
        vol = volume_status.get(chat_id, 100) - 10
        if vol < 0:
            vol = 0
        volume_status[chat_id] = vol
        await call.set_volume(chat_id, vol)
        await callback.answer(f"🔉 {vol}%", True)
    elif data == "seek_back":
        if current_track.get(chat_id):
            await callback.answer("⏪ -10s", True)
            try:
                await call.stop_stream(chat_id)
                await call.play(chat_id, MediaStream(current_track[chat_id]['url']))
            except: pass
    elif data == "seek_forward":
        if current_track.get(chat_id):
            await callback.answer("⏩ +10s", True)
            try:
                await call.stop_stream(chat_id)
                await call.play(chat_id, MediaStream(current_track[chat_id]['url']))
            except: pass
    elif data == "save_track":
        if not current_track.get(chat_id):
            return await callback.answer("Nothing playing", True)
        uid = str(user_id)
        if "saved" not in db:
            db["saved"] = {}
        if uid not in db["saved"]:
            db["saved"][uid] = []
        song = current_track[chat_id]
        if any(s['title'] == song['title'] for s in db["saved"][uid]):
            return await callback.answer("Already saved!", True)
        db["saved"][uid].append(song)
        save_data(db)
        await callback.answer(f"💾 Saved: {song['title']}", True)
    elif data == "add_playlist":
        if not current_track.get(chat_id):
            return await callback.answer("Nothing playing", True)
        uid = str(user_id)
        if "playlists" not in db:
            db["playlists"] = {}
        if uid not in db["playlists"]:
            db["playlists"][uid] = []
        song = current_track[chat_id]
        db["playlists"][uid].append(song)
        save_data(db)
        await callback.answer(f"📀 Added to Playlist: {song['title']}", True)

# ============================================================
# 📢 START, HELP, PING
# ============================================================

@bot.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    text = (
        "<b>✨ VΛNIX MUSIC - GOD EDITION ✨</b>\n"
        "<b>▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔</b>\n\n"
        "🎵 <b>The Ultimate Music + Management Bot</b>\n"
        "• Crystal Clear Audio & Video\n"
        "• Personal Playlist (Never Deletes)\n"
        "• Full Admin Controls\n\n"
        "🚀 <b>Try These:</b>\n"
        "/play - Play audio\n"
        "/vplay - Play video\n"
        "/playlist - Your saved songs\n"
        "/settings - Group settings"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Add to Group", url=f"https://t.me/VanixMusicBot?startgroup=true")],
        [InlineKeyboardButton("📖 Help", callback_data="help_menu")]
    ])
    await message.reply(text, reply_markup=keyboard, parse_mode="html")

@bot.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    text = (
        "<b>🎯 ALL COMMANDS</b>\n\n"
        "<b>🎶 Music</b>\n"
        "/play, /vplay, /pause, /resume, /skip\n"
        "/stop, /loop, /shuffle, /queue, /remove\n"
        "/volume, /seek, /save, /saved\n\n"
        "<b>📀 Playlist</b>\n"
        "/playlist add, /playlist list\n"
        "/playlist remove, /playlist clear\n\n"
        "<b>🛠️ Admin</b>\n"
        "/ban, /unban, /mute, /unmute, /kick\n"
        "/promote, /demote, /warn, /unwarn\n"
        "/setwelcome, /delwelcome, /setgoodbye\n"
        "/settings\n\n"
        "<b>ℹ️ Info</b>\n"
        "/start, /help, /ping"
    )
    await message.reply(text, parse_mode="html")

@bot.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = datetime.now()
    msg = await message.reply("🏓 Pinging...")
    end = datetime.now()
    await msg.edit(f"🏓 Pong! Latency: {(end-start).microseconds/1000:.2f}ms")

# ============================================================
# 🚀 MAIN (FIXED - NO 'return' on User Failure)
# ============================================================

async def main():
    print("✨ VΛNIX GOD EDITION STARTING ✨")
    print(f"📂 Data file path: {DATA_FILE}")
    
    await bot.start()
    print("✅ Bot Client Started.")
    
    global call
    if SESSION_STRING:
        try:
            await user.start()
            print("✅ User Client Started.")
            call = PyTgCalls(user)
            await call.start()
            asyncio.create_task(stream_monitor())
            print("✅ PyTgCalls Started.")
        except Exception as e:
            print(f"❌ User Client Failed: {e}")
            print("⚠️ Bot will run in TEXT-ONLY mode. Music commands will not work.")
    else:
        print("⚠️ SESSION_STRING not set. Bot will run in text-only mode.")
    
    print("🚀 Bot is LIVE on Railway!")
    await idle()
    
    await bot.stop()
    if user:
        await user.stop()

if __name__ == "__main__":
    asyncio.run(main())
