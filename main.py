import asyncio
import re
from telethon import TelegramClient, events, Button
from aiohttp import web

# معلومات حساب تيليجرام
api_id = 29721100
api_hash = '8e084daf57bd8ed1f6aded90f6ce4dac'
session_name = 'my_session'

# تعريف القنوات والصيغ والبوتات
channels_config = {
    "ichancy_saw": {
        "username": "ichancy_saw",
        "regex": r"(ctSh[0-9A-Za-z]+)",
        "bot": "@ichancy_saw_bot"
    },
    "ichancyTheKing": {
        "username": "ichancyTheKing",
        "regex": r"(0Kingg0boot0)",
        "bot": "@Ichancy_TheKingBot"
    },
    "ichancy_Bot_Dragon": {
        "username": "ichancy_Bot_Dragon",
        "regex": r"الكود:\s*([a-zA-Z0-9]+)",
        "bot": "@ichancy_dragon_bot"
    },
    "basel2255": {
        "username": "basel2255",
        "regex": r"الكود:\s*([a-zA-Z0-9*]+)",
        "bot": "@Ichancy_basel_bot"
    },
    "captain_ichancy": {
        "username": "captain_ichancy",
        "regex": r"[a-zA-Z0-9]+",
        "bot": "@ichancy_captain_bot",
        "pick_third": True  # نختار الكود الثالث
    }
}

# تهيئة العميل
client = TelegramClient(session_name, api_id, api_hash)
selected_channels = set()
monitoring_active = False

# start command
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    print("تم استقبال أمر /start")  # للتأكد من وصول الأمر
    keyboard = [
        [Button.inline(name, data=name.encode())] for name in channels_config
    ]
    keyboard.append([Button.inline("بدأ المراقبة", b"start_monitoring")])
    await event.reply("اختر القنوات التي تريد مراقبتها ثم اضغط 'بدأ المراقبة':", buttons=keyboard)

# stop command
@client.on(events.NewMessage(pattern='/stop'))
async def stop_handler(event):
    global monitoring_active
    selected_channels.clear()
    monitoring_active = False
    await event.respond("تم إيقاف المراقبة.")

# التعامل مع الأزرار
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global monitoring_active

    data = event.data.decode()
    if data == "start_monitoring":
        if not selected_channels:
            await event.answer("اختر قناة واحدة على الأقل!", alert=True)
            return
        monitoring_active = True
        await event.respond("تم تفعيل المراقبة بنجاح.")
    elif data in channels_config:
        if data in selected_channels:
            selected_channels.remove(data)
            await event.answer(f"تمت إزالة {data}")
        else:
            selected_channels.add(data)
            await event.answer(f"تمت إضافة {data}")

# مراقبة الرسائل الجديدة
@client.on(events.NewMessage)
async def monitor_handler(event):
    global monitoring_active
    if not monitoring_active:
        return

    for channel_name in selected_channels:
        config = channels_config[channel_name]
        if event.chat.username != config["username"]:
            continue

        match = re.findall(config["regex"], event.message.message)
        if match:
            if config.get("pick_third") and len(match) >= 3:
                code = match[2]
            else:
                code = match[0]
            await client.send_message(config["bot"], code)
            print(f"أُرسل الكود: {code} إلى {config['bot']}")
            break

# Web service للتأكد أن السيرفر شغال
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

# تشغيل البوت والسيرفر معًا
async def start_all():
    await client.start()
    print("Bot is running...")

    # تشغيل البوت في الخلفية
    client_loop = asyncio.create_task(client.run_until_disconnected())

    # تشغيل السيرفر aiohttp
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Web server is running on http://0.0.0.0:8080")

    await client_loop  # انتظر انتهاء البوت

if __name__ == "__main__":
    asyncio.run(start_all())
