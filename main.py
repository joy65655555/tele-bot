import asyncio
import re
from telethon import TelegramClient, events
from telethon.tl.custom import Button
from aiohttp import web

# بيانات حسابك الشخصي (وليس البوت)
api_id = 29721100
api_hash = '8e084daf57bd8ed1f6aded90f6ce4dac'
session_name = 'my_session'  # نفس اسم الجلسة يلي دخلت فيها رقمك

# تعريف القنوات
channels_config = {
    "ichancy_saw": {
        "username": "ichancy_saw",
        "regex": r"ctSh[0-9A-Za-z]+",
        "bot": "@ichancy_saw_bot"
    },
    "ichancyTheKing": {
        "username": "ichancyTheKing",
        "regex": r"0Kingg0boot0",
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
        "regex": r"([a-zA-Z0-9]+)",
        "bot": "@ichancy_captain_bot"
    }
}

# تحديد البوت
client = TelegramClient(session_name, api_id, api_hash)

# متغير لتحديد حالة المراقبة
monitoring_active = False
selected_channels = []

# دالة لمراقبة القنوات
async def start_monitoring(event, selected_channels):
    global monitoring_active
    if not monitoring_active:
        await event.reply("تم البدء بمراقبة القنوات المحددة.")
        monitoring_active = True

        @client.on(events.NewMessage(chats=[channels_config[channel]["username"] for channel in selected_channels]))
        async def channel_handler(event):
            if monitoring_active:
                message = event.message.message
                for channel in selected_channels:
                    regex = channels_config[channel]["regex"]
                    bot = channels_config[channel]["bot"]

                    match = re.search(regex, message)
                    if match:
                        code = match.group(1)
                        print(f"تم استخراج الكود: {code}")
                        await client.send_message(bot, code)
                # بعد التقاط الكود، نوقف المراقبة
                monitoring_active = False
                await event.reply("تم إرسال الكود بنجاح! وسيتوقف البوت الآن.")
                await client.disconnect()

    else:
        await event.reply("البوت يعمل بالفعل، انتظر حتى يتوقف ثم حاول مرة أخرى.")

# دالة لإيقاف المراقبة
async def stop_monitoring(event):
    global monitoring_active
    if monitoring_active:
        monitoring_active = False
        await event.reply("تم إيقاف المراقبة.")
    else:
        await event.reply("البوت ليس قيد التشغيل.")

# دالة لعرض قائمة القنوات
async def start_handler(event):
    keyboard = [
        [Button.inline(name, data=name.encode())] for name in channels_config.keys()
    ]
    await event.reply("اختر قناة لمراقبتها:", buttons=keyboard)

# استقبال الردود من الأزرار
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global selected_channels
    channel_name = event.data.decode("utf-8")

    if channel_name in channels_config:
        if channel_name not in selected_channels:
            selected_channels.append(channel_name)
            await event.answer(f"تم إضافة {channel_name} للمراقبة.")
        else:
            selected_channels.remove(channel_name)
            await event.answer(f"تم إزالة {channel_name} من المراقبة.")

# إعداد Web Service باستخدام aiohttp
async def handle(request):
    return web.Response(text="البوت يعمل!")

app = web.Application()
app.router.add_get('/', handle)

# دالة لبدء العميل
async def main():
    await client.start()
    print("البوت جاهز وينتظر أمر /start منك...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    web.run_app(app, port=8080)
