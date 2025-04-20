from telethon import TelegramClient, events, Button
import re
import asyncio

api_id = 29721100
api_hash = '8e084daf57bd8ed1f6aded90f6ce4dac'
session_name = 'my_session'

client = TelegramClient(session_name, api_id, api_hash)

# تعريف القنوات والبوتات والصيغ
channels_info = {
    'ichancy_saw': {
        'bot': '@ichancy_saw_bot',
        'extractor': lambda msg: re.search(r'\b[a-zA-Z]{2}\w{6}\b', msg)
    },
    'ichancyTheKing': {
        'bot': '@Ichancy_TheKingBot',
        'extractor': lambda msg: re.search(r'\b0\w{8}0\b', msg)
    },
    'ichancy_Bot_Dragon': {
        'bot': '@ichancy_dragon_bot',
        'extractor': lambda msg: re.search(r'الكود[:：]?\s*([a-zA-Z0-9]+)', msg)
    },
    'basel2255': {
        'bot': '@Ichancy_basel_bot',
        'extractor': lambda msg: re.search(r'الكود[:：]?\s*([a-zA-Z0-9*]+)', msg)
    },
    'captain_ichancy': {
        'bot': '@ichancy_captain_bot',
        'extractor': lambda msg: re.findall(r'\b[a-zA-Z0-9]{8}\b', msg)
    }
}

# القنوات التي يتم مراقبتها حالياً
active_channels = set()

@client.on(events.NewMessage(pattern='/start'))
async def handle_start(event):
    buttons = [Button.inline(name, data=name.encode()) for name in channels_info]
    await event.respond("اختر القنوات التي تريد مراقبتها:", buttons=buttons)

@client.on(events.NewMessage(pattern='/stop'))
async def handle_stop(event):
    active_channels.clear()
    await event.respond("تم إيقاف المراقبة لجميع القنوات.")

@client.on(events.CallbackQuery)
async def handle_callback(event):
    channel = event.data.decode()
    if channel in active_channels:
        await event.answer("هذه القناة مفعّلة بالفعل.", alert=True)
        return

    active_channels.add(channel)
    await event.answer(f"بدأت المراقبة لقناة {channel}")
    await event.respond(f"سيتم مراقبة قناة {channel} الآن...")

@client.on(events.NewMessage)
async def monitor_channels(event):
    if not active_channels:
        return

    sender = await event.get_chat()
    if sender.username not in active_channels:
        return

    channel_data = channels_info.get(sender.username)
    if not channel_data:
        return

    extractor = channel_data['extractor']
    match = extractor(event.message.message)

    if sender.username == 'captain_ichancy' and isinstance(match, list):
        if len(match) >= 3:
            code = match[2]
        else:
            return
    elif match:
        code = match.group(1) if hasattr(match, 'group') else match
    else:
        return

    print(f"كود مستخرج من {sender.username}: {code}")
    await client.send_message(channel_data['bot'], code)

async def main():
    await client.start()
    print("البوت جاهز...")
    await client.run_until_disconnected()

asyncio.run(main())
