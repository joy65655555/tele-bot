import asyncio
from aiohttp import web
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import re

# بيانات حسابك في تلغرام
api_id = 29721100
api_hash = '8e084daf57bd8ed1f6aded90f6ce4dac'
session_name = 'my_session'

# تهيئة البوت
client = TelegramClient(session_name, api_id, api_hash)

# القنوات والبوتات المرتبطة بها
channels_config = {
    'ichancy_saw': {
        'bot': '@ichancy_saw_bot',
        'pattern': r'([a-zA-Z0-9]+)',  # صيغة الكود في هذه القناة
    },
    'ichancyTheKing': {
        'bot': '@Ichancy_TheKingBot',
        'pattern': r'(\d+[a-zA-Z]+\d+)',  # صيغة الكود في هذه القناة
    },
    'ichancy_Bot_Dragon': {
        'bot': '@ichancy_dragon_bot',
        'pattern': r'الكود[:：]?\s*([a-zA-Z0-9]+)',  # صيغة الكود في هذه القناة
    },
    'basel2255': {
        'bot': '@Ichancy_basel_bot',
        'pattern': r'الكود[:：]?\s*([a-zA-Z0-9*]+)',  # صيغة الكود في هذه القناة
    },
    'captain_ichancy': {
        'bot': '@ichancy_captain_bot',
        'pattern': r'([a-zA-Z0-9]+)',  # صيغة الكود في هذه القناة (اختيار الكود الثالث)
    }
}

# متغير لتخزين القناة المراقبة الحالية
monitoring_channel = None

# هذا معالج الأمر /start ويعرض القنوات للمستخدم
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    keyboard = [
        [Button.inline(name, data=name.encode())] for name in channels_config.keys()
    ]
    await event.respond(
        'اختر قناة لمراقبتها:',
        buttons=keyboard
    )

# معالج الأزرار، يقوم بمعالجة القناة المختارة
@client.on(events.CallbackQuery)
async def callback_handler(event):
    global monitoring_channel
    selected_channel = event.data.decode('utf-8')
    monitoring_channel = selected_channel

    if monitoring_channel:
        await event.answer(f"تم اختيار القناة: {selected_channel}")
        # تبدأ المراقبة على القناة المحددة
        await start_monitoring(selected_channel)
    else:
        await event.answer("حدث خطأ، يرجى المحاولة مجددًا.")

# بدء المراقبة على القناة المحددة
async def start_monitoring(channel_name):
    bot_name = channels_config[channel_name]['bot']
    pattern = channels_config[channel_name]['pattern']

    # مراقبة القناة المختارة
    @client.on(events.NewMessage(chats=channel_name))
    async def channel_handler(event):
        message = event.message.message
        print(f"رسالة جديدة من القناة {channel_name}:\n{message}")

        # استخدام regex لاستخراج الكود بناءً على الصيغة المحددة
        match = re.search(pattern, message)
        if match:
            code = match.group(1)
            print(f"تم استخراج الكود: {code}")
            await client.send_message(bot_name, code)
        else:
            print("لم يتم العثور على كود.")

# معالج الأمر /stop لإيقاف المراقبة
@client.on(events.NewMessage(pattern='/stop'))
async def stop_handler(event):
    global monitoring_channel
    monitoring_channel = None
    await event.respond("تم إيقاف المراقبة.")

# إعداد الخدمة كـ Web Service باستخدام aiohttp
async def init_app():
    app = web.Application()

    # أي صفحة ويب أو مسار ترغب في إضافته
    async def handle(request):
        return web.Response(text="خدمة الويب تعمل بنجاح!")

    app.router.add_get('/', handle)

    # إرجاع التطبيق ليعمل مع aiohttp
    return app

# دالة لبدء كل شيء (التطبيق و البوت)
async def main():
    # بدء تشغيل الخدمة كـ Web Service
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    # بدء البوت
    await client.start()
    print("البوت جاهز على التفاعل!")

    # تشغيل البوت بشكل غير متزامن
    await client.run_until_disconnected()

# تشغيل التطبيق
asyncio.run(main())
