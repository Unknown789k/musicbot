"""
✧･ﾟ: *✧･ﾟ:*  VΛПIΧ MЦSIC BӨƬ  *:･ﾟ✧*:･ﾟ✧
         ⋆⋅☆⋅⋆  Premium Edition  ⋆⋅☆⋅⋆
"""

import asyncio
import os
import re
from typing import Dict, List, Optional
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from pyrogram.enums import ChatMemberStatus, ChatType
from pytgcalls import PyTgCalls, idle
from pytgcalls.types import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall
import yt_dlp

# ============================================================
# ⚙️ CONFIGURATION - YAHAN APNI INFO DAALEIN
# ============================================================

API_ID = 12345                      # my.telegram.org se
API_HASH = "your_api_hash"          # my.telegram.org se
BOT_TOKEN = "your_bot_token"        # @BotFather se
SESSION_STRING = "your_session_string"  # Pyrogram session
OWNER_ID = 123456789                # Aapka Telegram user ID

# Bot ka naam aur username
BOT_NAME = "VΛПIΧ MЦSIC BӨƬ"
BOT_USERNAME = "@vanixmusic_bot"

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

# ============================================================
# 🎶 PLAYBACK ENGINE
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
    text = (
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n"
        f"<b>   ⋆⋅☆⋅⋆  𝑵𝑶𝑾 𝑷𝑳𝑨𝒀𝑰𝑵𝑮  ⋆⋅☆⋅⋆</b>\n"
        f"<b>✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧ ✧</b>\n\n"
        f"<b>✦ 𝑻𝒊𝒕𝒍𝒆:</b> <a href='{song['webpage_url']}'>{song['title']}</a>\n"
        f"<b>⏱ 𝑫𝒖𝒓𝒂𝒕𝒊𝒐𝒏:</b> <code>{song['duration_str']}</code>\n"
        f"<b>👤 𝑼𝒑𝒍𝒐𝒂𝒅𝒆𝒓:</b> {song['uploader']}\n"
        f"<b>👀 𝑽𝒊𝒆𝒘𝒔:</b> {song['view_count']:,}\n\n"
        f"<b>📊 𝑸𝒖𝒆𝒖𝒆:</b> <code>{len(queues.get(chat_id, []))}</code> songs remaining"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ 𝑷𝒂𝒖𝒔𝒆", callback_data="pause"),
            InlineKeyboardButton("▶️ 𝑹𝒆𝒔𝒖𝒎𝒆", callback_data="resume"),
        ],
        [
            InlineKeyboardButton("⏭ 𝑺𝒌𝒊𝒑", callback_data="skip"),
            InlineKeyboardButton("🔁 𝑳𝒐𝒐𝒑", callback_data="loop"),
        ],
        [
            InlineKeyboardButton("⏹ 𝑺𝒕𝒐𝒑", callback_data="stop"),
            InlineKeyboardButton("📋 𝑸𝒖𝒆𝒖𝒆", callback_data="queue"),
        ],
        [
            InlineKeyboardButton("📢 𝑺𝒖𝒑𝒑𝒐𝒓𝒕", url="https://t.me/vanixsupport"),
            InlineKeyboardButton("👨‍💻 𝑶𝒘𝒏𝒆𝒓", url="https://t.me/vanixowner"),
        ]
    ])
    
    await app.send_message(chat_id, text, reply_markup=keyboard, parse_mode="html", disable_web_page_preview=True)

# ============================================================
# 📡 STREAM END HANDLER
# ============================================================

@call.on_stream_end()
async def stream_end_handler(chat_id: int):
    await play_next(chat_id)

# ============================================================
# 🎮 COMMANDS
# ============================================================

# ---------- /start ----------
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply(
        f"<b>✧･ﾟ: *✧･ﾟ:*  𝑽𝑨𝑵𝑰𝑿 𝑴𝑼𝑺𝑰𝑪 𝑩𝑶𝑻  *:･ﾟ✧*:･ﾟ✧</b>\n\n"
        f"<b>✦ 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑴𝒖𝒔𝒊𝒄 𝑺𝒕𝒓𝒆𝒂𝒎𝒊𝒏𝒈 𝑩𝒐𝒕 ✦</b>\n\n"
        f"<b>🎯 𝑯𝒐𝒘 𝒕𝒐 𝑼𝒔𝒆</b>\n"
        f"➤ <code>/play &lt;song&gt;</code> - Play a song\n"
        f"➤ <code>/fplay &lt;song&gt;</code> - Force play (skip current)\n"
        f"➤ <code>/pause</code> - Pause playback\n"
        f"➤ <code>/resume</code> - Resume playback\n"
        f"➤ <code>/skip</code> - Skip current song\n"
        f"➤ <code>/stop</code> - Stop & clear queue\n"
        f"➤ <code>/loop</code> - Toggle loop mode\n"
        f"➤ <code>/queue</code> - View queue\n"
        f"➤ <code>/radio</code> - Live radio stations\n"
        f"➤ <code>/ping</code> - Check bot status\n\n"
        f"<b>✨ 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑭𝒆𝒂𝒕𝒖𝒓𝒆𝒔</b>\n"
        f"• Multi-platform support (YouTube/Spotify/SoundCloud)\n"
        f"• Advanced queue management\n"
        f"• Loop mode (repeat one song)\n"
        f"• Live radio streaming\n"
        f"• Admin controls\n\n"
        f"<b>📢 Support:</b> @vanixsupport\n"
        f"<b>👨‍💻 Owner:</b> @vanixowner",
        parse_mode="html",
        disable_web_page_preview=True
    )

# ---------- /play ----------
@app.on_message(filters.command(["play", "p"]))
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/play &lt;song name or link&gt;</code>", parse_mode="html")
        return
    
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    
    msg = await message.reply("🔍 <b>Searching...</b> Please wait.", parse_mode="html")
    
    try:
        song_info = await get_audio_info(query)
    except Exception as e:
        await msg.edit(f"❌ <b>Error:</b> <code>{str(e)}</code>", parse_mode="html")
        return
    
    if chat_id not in queues:
        queues[chat_id] = []
    
    if not current_track.get(chat_id):
        queues[chat_id].append(song_info)
        await msg.edit(
            f"✅ <b>{song_info['title']}</b> added to queue.\n"
            f"▶️ <i>Now playing...</i>",
            parse_mode="html"
        )
        await play_next(chat_id)
    else:
        position = len(queues[chat_id]) + 1
        queues[chat_id].append(song_info)
        await msg.edit(
            f"✅ <b>{song_info['title']}</b> added to queue.\n"
            f"📊 <b>Position:</b> <code>{position}</code>",
            parse_mode="html"
        )

# ---------- /fplay ----------
@app.on_message(filters.command(["fplay", "fp"]))
async def force_play_command(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("❌ <b>Usage:</b> <code>/fplay &lt;song name or link&gt;</code>", parse_mode="html")
        return
    
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    
    msg = await message.reply("🔍 <b>Searching...</b>", parse_mode="html")
    
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
    
    queues[chat_id].insert(0, song_info)
    current_track[chat_id] = {}
    
    await msg.edit(
        f"⏭ <b>Force playing:</b> {song_info['title']}",
        parse_mode="html"
    )
    await play_next(chat_id)

# ---------- /pause ----------
@app.on_message(filters.command("pause"))
async def pause_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.pause_stream(chat_id)
        playing_status[chat_id] = False
        await message.reply("⏸ <b>Paused</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

# ---------- /resume ----------
@app.on_message(filters.command("resume"))
async def resume_command(client: Client, message: Message):
    chat_id = message.chat.id
    try:
        await call.resume_stream(chat_id)
        playing_status[chat_id] = True
        await message.reply("▶️ <b>Resumed</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

# ---------- /skip ----------
@app.on_message(filters.command(["skip", "next"]))
async def skip_command(client: Client, message: Message):
    chat_id = message.chat.id
    if not current_track.get(chat_id):
        await message.reply("❌ <b>Nothing is playing.</b>", parse_mode="html")
        return
    
    current_track[chat_id] = {}
    try:
        await call.stop_stream(chat_id)
    except:
        pass
    await play_next(chat_id)
    await message.reply("⏭ <b>Skipped</b>", parse_mode="html")

# ---------- /stop ----------
@app.on_message(filters.command(["stop", "end"]))
async def stop_command(client: Client, message: Message):
    chat_id = message.chat.id
    queues[chat_id] = []
    current_track[chat_id] = {}
    loop_status[chat_id] = False
    playing_status[chat_id] = False
    try:
        await call.leave_call(chat_id)
        await message.reply("⏹ <b>Stopped and left VC</b>", parse_mode="html")
    except Exception as e:
        await message.reply(f"❌ <code>{str(e)}</code>", parse_mode="html")

# ---------- /loop ----------
@app.on_message(filters.command("loop"))
async def loop_command(client: Client, message: Message):
    chat_id = message.chat.id
    current = loop_status.get(chat_id, False)
    loop_status[chat_id] = not current
    status = "𝑶𝑵 🔁" if loop_status[chat_id] else "𝑶𝑭𝑭 ➡️"
    await message.reply(f"🔄 <b>Loop:</b> <code>{status}</code>", parse_mode="html")

# ---------- /queue ----------
@app.on_message(filters.command(["queue", "q"]))
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    if not queues.get(chat_id) and not current_track.get(chat_id):
        await message.reply("📭 <b>Queue is empty</b>", parse_mode="html")
        return
    
    text = "<b>✦ 𝗤𝗨𝗘𝗨𝗘 𝗟𝗜𝗦𝗧 ✦</b>\n\n"
    
    if current_track.get(chat_id):
        text += f"<b>▶️ 𝑵𝒐𝒘 𝑷𝒍𝒂𝒚𝒊𝒏𝒈:</b>\n"
        text += f"   ✦ {current_track[chat_id]['title']}\n"
        text += f"   ⏱ <code>{current_track[chat_id]['duration_str']}</code>\n\n"
    
    if queues.get(chat_id):
        text += "<b>⏩ 𝑼𝒑 𝑵𝒆𝒙𝒕:</b>\n"
        for i, song in enumerate(queues[chat_id][:15], 1):
            text += f"<code>{i}.</code> {song['title']} <code>[{song['duration_str']}]</code>\n"
        if len(queues[chat_id]) > 15:
            text += f"\n... and <code>{len(queues[chat_id])-15}</code> more"
    
    await message.reply(text, parse_mode="html")

# ---------- /ping ----------
@app.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = datetime.now()
    msg = await message.reply("🏓 <b>Pinging...</b>", parse_mode="html")
    end = datetime.now()
    latency = (end - start).microseconds / 1000
    await msg.edit(
        f"🏓 <b>Pong!</b>\n"
        f"⚡ <b>Latency:</b> <code>{latency:.2f}ms</code>",
        parse_mode="html"
    )

# ---------- /radio ----------
@app.on_message(filters.command("radio"))
async def radio_command(client: Client, message: Message):
    await message.reply(
        "<b>📻 𝑳𝒊𝒗𝒆 𝑹𝒂𝒅𝒊𝒐 𝑺𝒕𝒂𝒕𝒊𝒐𝒏𝒔</b>\n\n"
        "Use <code>/play</code> with these links:\n"
        "• <code>https://youtu.be/4JipHEz53sU</code> - Lofi Girl\n"
        "• <code>https://youtu.be/5qap5aO4i9A</code> - Chillhop\n"
        "• <code>https://youtu.be/DWcJFNfaw9c</code> - Jazz\n"
        "• <code>https://youtu.be/UjJXw-9hTdQ</code> - Classic Rock\n\n"
        "Or paste any M3U8/radio stream URL!",
        parse_mode="html"
    )

# ---------- /help ----------
@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply(
        f"<b>✧･ﾟ: *✧･ﾟ:*  𝑽𝑨𝑵𝑰𝑿 𝑴𝑼𝑺𝑰𝑪 𝑩𝑶𝑻  *:･ﾟ✧*:･ﾟ✧</b>\n\n"
        f"<b>🎯 𝑪𝒐𝒎𝒎𝒂𝒏𝒅𝒔</b>\n"
        f"➤ <code>/play &lt;song&gt;</code> - Play music\n"
        f"➤ <code>/fplay &lt;song&gt;</code> - Force play\n"
        f"➤ <code>/pause</code> - Pause\n"
        f"➤ <code>/resume</code> - Resume\n"
        f"➤ <code>/skip</code> - Skip\n"
        f"➤ <code>/stop</code> - Stop\n"
        f"➤ <code>/loop</code> - Loop toggle\n"
        f"➤ <code>/queue</code> - View queue\n"
        f"➤ <code>/radio</code> - Live radio\n"
        f"➤ <code>/ping</code> - Check status\n\n"
        f"<b>📢 Support:</b> @vanixsupport\n"
        f"<b>👨‍💻 Owner:</b> @vanixowner",
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
            playing_status[chat_id] = False
            await callback.answer("⏸ Paused", show_alert=True)
        except Exception as e:
            await callback.answer(f"Error: {e}", show_alert=True)
    
    elif data == "resume":
        try:
            await call.resume_stream(chat_id)
            playing_status[chat_id] = True
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
        status = "ON" if loop_status[chat_id] else "OFF"
        await callback.answer(f"Loop: {status}", show_alert=True)
    
    elif data == "stop":
        queues[chat_id] = []
        current_track[chat_id] = {}
        loop_status[chat_id] = False
        playing_status[chat_id] = False
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
    print("📊 Commands: /play, /pause, /skip, /stop, /loop, /queue")
    print("🤖 Press Ctrl+C to stop")
    
    await idle()

if __name__ == "__main__":
    asyncio.run(main())