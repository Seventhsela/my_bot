import asyncio
import asyncpg
import random
import os
from aiogram import Bot

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Ссылка на базу данных
DATABASE_URL = os.getenv('DATABASE_URL')

# Список возможных напоминаний
REMINDER_MESSAGES = [
    "Привет! Не хочешь немного пообщаться со мной? Просто выбери функцию '🧠 Общение с ИИ-компаньоном'", 
    "Я тут скучаю... Загляни ко мне!",
    "Эй, как твои дела? Давай поболтаем! Просто выбери функцию '🧠 Общение с ИИ-компаньоном'",
    "Я всегда на связи, если захочешь поговорить :)",
    "Помнишь про меня? Я всё ещё здесь, жду твоего сообщения!",
    "Что-то тебя не видно, все хорошо?",
    "Расскажи как прошел твой день, просто выбери функцию '🧠 Общение с ИИ-компаньоном'",
    "Я чувствую тебе нужна мотивоционная речь от наставника. Начни разговор с ИИ-наставником, просто выбрав функцию '🧠 Общение с ИИ-компаньоном'",
    "Возможно ты нуждаешься в консультанции у психолога. Начни разговор с ИИ-психологом, просто выбрав функцию '🧠 Общение с ИИ-компаньоном'",
    "Не забывай выполнять дыхательные практики! Я тебе с этим помогу!",
    "Узнай у меня о советах по снижению тревожности",
    "Если ищешь психолога в Кокшетау, я здесь!"
]

async def send_reminders():
    bot = Bot(token=BOT_TOKEN)

    conn = await asyncpg.connect(DATABASE_URL)
    users = await conn.fetch("SELECT user_id FROM users")

    for user in users:
        user_id = user['user_id']
        message = random.choice(REMINDER_MESSAGES)  
        try:
            await bot.send_message(user_id, message)
        except Exception as e:
            print(f"Не удалось отправить {user_id}: {e}")

    await conn.close()
    await bot.session.close()

asyncio.run(send_reminders())
