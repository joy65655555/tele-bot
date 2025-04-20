import asyncio
from aiohttp import web
from telethon import TelegramClient, events
from telethon.tl.custom import Button

# بيانات حسابك في تلغرام
api_id = 29721100
api_hash = '8e084daf57bd8ed1f6aded90f6ce4dac'
session_name = 'my_session'

# تهيئة البوت
client = TelegramClient(session_name, api_id, api_hash)

# القنوات والبوتات المرتبطة بها
channels_config = {
    'ichancy_saw': '@ichancy_saw_bot',
    'ichancyTheKing': '@Ichancy_TheKingBot',
    'ichancy_Bot_Dragon': '@ichancy_dragon_bot',
    'basel2255': '@Ichancy_basel_bot',
    'captain_ichancy': '@ichancy_captain_bot'
}

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
    selected_channel = event.data.decode('utf-8')
    bot_name = channels_config.get(selected_channel)

    if bot_name:
        await event.answer(f"تم اختيار القناة: {selected_channel}")
        # هنا يمكنك إضافة الكود الخاص بمراقبة القناة المختارة
    else:
        await event.answer("حدث خطأ، يرجى المحاولة مجددًا.")

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
