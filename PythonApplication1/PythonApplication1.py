import asyncio
import traceback
import os

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

if not api_id or not api_hash:
    print("⚙️ Налаштування Telegram API")
    api_id = input("Введи свій api_id: ").strip()
    api_hash = input("Введи свій api_hash: ").strip()
    
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f"API_ID={api_id}\n")
        f.write(f"API_HASH={api_hash}\n")
    print("✔️ Дані збережені у .env!")
    load_dotenv(override=True)

client = TelegramClient("session", int(api_id), api_hash)

# ChatsNoColdown = ['@Tist_3']
# ChatsColdown = ['@Tist_1', '@Tist_2'] 
# ChatsFork = { "@Tist_4": 2 }

ChatsNoColdown = [ '@vicemshop', '@crarizonarp' ]
ChatsColdown = [ '@arz_vice' ]
ChatsFork = { '@arzmarket_vice': 2150290 }


async def get_slowmode_remaining_seconds(chat):
    entity = await client.get_entity(chat)
    full = await client(GetFullChannelRequest(entity))

    next_date = full.full_chat.slowmode_next_send_date

    if not next_date:
        return 0

    now = datetime.now(timezone.utc)

    remaining = (next_date - now).total_seconds()

    return max(0, int(remaining))

async def SendMessage(chat, timer_type):
    print(f"✔️Чат {chat} активний")

    topic_id = None
    if timer_type == "extended_timers":
        topic_id = ChatsFork.get(chat)

    while True:
        try:
            with open('Message.txt', 'r', encoding='utf-8') as f:
                message_text = f.read().strip()
        except FileNotFoundError:
            print("Файл message.txt не знайдено!")
            break
        
        try:

            entity = await client.get_entity(chat)
            full = await client(GetFullChannelRequest(entity))

            next_send = full.full_chat.slowmode_next_send_date

            if timer_type == "without_timer":             
                await client.send_message(chat, message_text, parse_mode="html", file="Photo_1.jpg")  
                print(f"✔️Чат {chat}: Успішно відправив повідомлення, пішов спати до 600 c.")
                await asyncio.sleep(600)

            if timer_type == "simple_timers" and await get_slowmode_remaining_seconds(chat) == 0:
                await client.send_message(chat, message_text, parse_mode="html", file="Photo_1.jpg")

                entity = await client.get_entity(chat)
                full = await client(GetFullChannelRequest(entity))
                next_send = full.full_chat.slowmode_next_send_date

                print(f"✔Чат {chat}: Успішно відправив повідомлення, пішов спати до {next_send}")
            elif timer_type == "simple_timers":
                print(f"❗Чат {chat}: Незміг відправити повідомлення, сплю до {next_send}")

            if timer_type == "extended_timers" and await get_slowmode_remaining_seconds(chat) == 0:
                await client.send_message(chat, message_text, parse_mode="html", reply_to=topic_id, file="Photo_1.jpg")

                entity = await client.get_entity(chat)
                full = await client(GetFullChannelRequest(entity))
                next_send = full.full_chat.slowmode_next_send_date

                print(f"✔Чат {chat}: Успішно відправив повідомлення, пішов спати до {next_send}")
            elif timer_type == "simple_timers":
                print(f"❗Чат {chat}: Незміг відправити повідомлення, сплю до {next_send}")

            await asyncio.sleep(await get_slowmode_remaining_seconds(chat))

        except Exception as e:
            print(f"❌Чат {chat}: Виникла помилка, дивись Log.txt")
            
            log_file = Path("Log.txt")
            log_file.touch(exist_ok=True)
            
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"=== {datetime.now()} ===\n")
                log.write(f"Чат: {chat}, Timer: {timer_type}\n")
                log.write("Помилка:\n")
                log.write(traceback.format_exc())
                log.write("\n\n")

async def main():
    tasks = []

    for Chat in ChatsNoColdown:
        tasks.append(SendMessage(Chat,"without_timer"))
    
    for Chat in ChatsColdown:
        tasks.append(SendMessage(Chat,"simple_timers"))
    
    for Chat in ChatsFork:
        tasks.append(SendMessage(Chat,"extended_timers"))

    await asyncio.gather(*tasks)


with client:
    client.loop.run_until_complete(main())