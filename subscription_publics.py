import asyncio
import pika
import json

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, InputPeerChannel, InputPeerChat
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.events import NewMessage
from telethon.utils import get_peer_id


from settings import (
    TG_API_ID, TG_API_HASH, TG_PHONE, RABBITMQ_USER, RABBITMQ_PASS, RABBITMQ_HOST, RABBITMQ_PORT,
    COMPANION_MESSAGE_QUEUE_NAME)


def send_message(message: str, link: str, source: str):
    credentials = pika.PlainCredentials(
        RABBITMQ_USER, RABBITMQ_PASS)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    ))

    channel = connection.channel()
    queue_name = COMPANION_MESSAGE_QUEUE_NAME

    # Объявляем очередь (идемпотентная операция)
    channel.queue_declare(queue=queue_name, durable=True)

    # Формируем сообщение
    payload = {
        'message': message,
        'link': link,
        'source': source
    }

    # Отправляем в очередь
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Персистентное сообщение
        )
    )

    print(f" [x] Sent: {payload}")
    connection.close()

async def message_callback_handler():
    """
    Основная функция для настройки callback обработки сообщений
    """
    client = TelegramClient('session_callback', TG_API_ID, TG_API_HASH)
    await client.start(TG_PHONE)

    print("✅ Успешно подключено к Telegram!")
    print("слушаю все сообщения во всех чатах...")

    @client.on(NewMessage())
    async def handle_new_message(event):
        """
        Эта функция будет вызываться при каждом новом сообщении
        """
        message = event.message
        chat = await event.get_chat()
        sender = await event.get_sender()

        # Базовая информация о сообщении
        chat_title = getattr(chat, 'title', 'Личный чат')
        if not message.text:
            return

        chat_id = chat.id
        sender_name = sender.first_name if sender else 'Неизвестный отправитель'
        message_text = message.text or '[Медиафайл/стicker]'

        message_link = None
        try:
            # В современных версиях Telethon есть встроенный атрибут link
            if hasattr(message, 'link') and message.link:
                message_link = message.link
            else:
                # Резервный способ для старых версий
                if hasattr(chat, 'username') and chat.username:
                    message_link = f"https://t.me/{chat.username}/{message.id}"
                elif hasattr(chat, 'id'):
                    # Для каналов и супергрупп: убираем префикс -100 вручную
                    real_chat_id = chat.id
                    if str(real_chat_id).startswith('-100'):
                        real_chat_id = int(str(real_chat_id)[4:])
                    message_link = f"https://t.me/c/{real_chat_id}/{message.id}"
        except Exception as e:
            print(f"❌ Ошибка при получении ссылки: {e}")

        send_message(
            message=message_text,
            link=message_link,
            source='telegram'
        )
        # Выводим информацию о сообщении
        print(f"\n{'=' * 60}")
        print(f"📩 НОВОЕ СООБЩЕНИЕ:")
        print(f"   📌 Чат: {chat_title} (ID: {chat_id})")
        print(f"   👤 Отправитель: {sender_name}")
        print(f"   🕒 Время: {message.date}")
        print(f"   💬 Текст: {message_text}")
        print(f"{'=' * 60}")


    print("\n🚀 Запущен режим прослушивания сообщений...")
    try:
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n🛑 Прослушивание остановлено пользователем")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    print("🤖 TELEGRAM MESSAGE LISTENER")

    asyncio.run(message_callback_handler())

# --- ЗДЕСЬ ВАША ЛОГИКА ОБРАБОТКИ СООБЩЕНИЯ ---

# # Пример 1: Автоответ на определенные ключевые слова
# if 'привет' in message_text.lower() or 'hello' in message_text.lower():
#     await message.reply('👋 Привет! Я автоматический обработчик сообщений.')
#     print("   ✅ Отправлен автоответ на приветствие")

# Пример 2: Логирование всех сообщений в файл
# log_message = f"[{message.date}] Чат: {chat_title}, Отправитель: {sender_name}, Текст: {message_text}\n"
# with open('messages_log.txt', 'a', encoding='utf-8') as f:
#     f.write(log_message)

# # Пример 3: Обработка команд
# if message_text.startswith('/'):
#     command = message_text.split()[0]
#     if command == '/help':
#         await message.reply('🤖 Доступные команды:\n/help - эта помощь\n/status - статус бота')
#     elif command == '/status':
#         await message.reply('✅ Все системы в норме!')
#
# # Пример 4: Фильтрация по конкретным чатам
# important_chat_ids = [-1001234567890, -1009876543210]  # ID важных чатов
# if chat_id in important_chat_ids:
#     print(f"   ⚠️ ВАЖНОЕ СООБЩЕНИЕ в чате {chat_title}!")
#     # Здесь можно отправить уведомление на почту или в другой сервис