from aiohttp import web
from telethon import TelegramClient, events
import asyncio
import re

api_id = 29721100
api_hash = '8e084daf57bd8ed1f6aded90f6ce4dac'
session_name = 'my_session'

client = TelegramClient(session_name, api_id, api_hash)

# القنوات والصيغ المرتبطة
channels_config = {
    "ichancy_saw": {
        "bot": "@ichancy_saw_bot",
        "regex": r"\b([a-zA-Z]{2}\w{5,})\b"
    },
    "ichancyTheKing": {
        "bot": "@Ichancy_TheKingBot",
        "regex": r"\b(0\w+0)\b"
    },
    "ichancy_Bot_Dragon": {
        "bot": "@ichancy_dragon_bot",
        "regex": r"الكود[:：]?\s*([a-zA-Z0-9]+)"
    },
    "basel2255": {
        "bot": "@Ichancy_basel_bot",
        "regex": r"الكود[:：]?\s*([a-zA-Z0-9*]+)"
    },
    "captain_ichancy": {
        "bot": "@ichancy_captain_bot",
        "regex": r"\b[a-zA-Z0-9]{8}\b",
        "select_index": 2  # الكود الثالث
    }
}

# مراقبة القنوات
active_channels = set()

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    keyboard = [
        [web.Button.inline(name, data=name.encode())] for name in channels_config.keys()
    ]
    await event.respond("اختر القنوات التي تريد مراقبتها:", buttons=keyboard)

@client.on(events.NewMessage(pattern='/stop'))
async def stop_handler(event):
    active_channels.clear()
    await event.respond("تم إيقاف مراقبة جميع القنوات.")

@client.on(events.CallbackQuery)
async def channel_selection_handler(event):
    channel = event.data.decode()
    if channel in active_channels:
        active_channels.remove(channel)
        await event.answer(f"تم إلغاء المراقبة: {channel}", alert=True)
    else:
        active_channels.add(channel)
        await event.answer(f"بدأت المراقبة: {channel}", alert=True)

@client.on(events.NewMessage)
async def message_handler(event):
    if event.chat and event.chat.username in active_channels:
        username = event.chat.username
        config = channels_config.get(username)
        if not config:
            return
        text = event.raw_text
        matches = re.findall(config['regex'], text)

        if matches:
            code = matches[config['select_index']] if username == "captain_ichancy" and len(matches) > 2 else matches[0]
            print(f"[{username}] تم استخراج الكود: {code}")
            await client.send_message(config['bot'], code)

# تشغيل Web Service من aiohttp
async def start_web_app():
    await client.start()
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text="Bot is running"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=8080)
    await site.start()
    print("Web service started on port 8080")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(start_web_app())
