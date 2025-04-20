from telethon import TelegramClient, events
import re
import asyncio

# بيانات حسابك الشخصي (وليس البوت)
api_id = 29721100
api_hash = '8e084daf57bd8ed1f6aded90f6ce4dac'
session_name = 'my_session'  # نفس اسم الجلسة يلي دخلت فيها رقمك

# اسم البوت يلي بدك تبعتله الكود
target_bot = '@Ichancy_TheKingBot'

# اسم القناة للمراقبة
channel_username = 'ichancyTheKing'

# هنا نبدأ العميل الشخصي
client = TelegramClient(session_name, api_id, api_hash)

# متغير لتحديد حالة المراقبة
monitoring_active = False

# هذا الحدث يستقبل رسالة /start من محادثتك مع البوت الخاص فيك
@client.on(events.NewMessage(pattern='/start'))
async def start_monitoring(event):
    global monitoring_active

    # التأكد من أن المرسل ليس بوت آخر
    sender = await event.get_sender()
    if sender.bot:  
        return

    if not monitoring_active:
        await event.reply("تم البدء بمراقبة القناة، سيتم التقاط أول كود يُنشر وإرساله للبوت.")
        monitoring_active = True

        # تبدأ المراقبة
        @client.on(events.NewMessage(chats=channel_username))
        async def channel_handler(event):
            if monitoring_active:
                message = event.message.message
                print(f"رسالة جديدة:\n{message}")

                match = re.search(r'الكود[:：]?\s*([a-zA-Z0-9]+)', message)
                if match:
                    code = match.group(1)
                    print(f"تم استخراج الكود: {code}")
                    await client.send_message(target_bot, code)
                else:
                    print("لم يتم العثور على كود.")
                
                # بعد التقاط الكود، نوقف المراقبة
                monitoring_active = False
                await event.reply("تم إرسال الكود بنجاح! وسيتوقف البوت الآن.")

                # نفصل البوت بعد التقاط أول رسالة
                await client.disconnect()
    else:
        await event.reply("البوت يعمل بالفعل، انتظر حتى يتوقف ثم حاول مرة أخرى.")

async def main():
    await client.start()
    print("البوت جاهز وينتظر أمر /start منك...")
    await client.run_until_disconnected()

asyncio.run(main())