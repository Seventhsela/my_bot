import logging
import asyncio
import re
import openai
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode, ChatAction
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from aiogram.client.default import DefaultBotProperties
import os
from dotenv import load_dotenv
from db import create_users_table
from db import save_user_style
from db import get_user_style

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class AIStyle(StatesGroup):
    choosing_style = State()
    chatting = State()

# logging
logging.basicConfig(level=logging.INFO)

# OpenAI key
openai.api_key = OPENAI_API_KEY

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Хранилище выбора стиля общения
user_styles = {}

# Старт
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("<b>Привет!</b> 👋\n\n"
    '''Похоже, ты оказался здесь не просто так. Возможно, тебя что-то тревожит, ты чувствуешь усталость или просто хочешь немного расслабиться.\nВ любом случае — ты по адресу!\n
    Я — бот, который поможет тебе почувствовать себя лучше. Сo мной ты сможешь:
• Выполнить дыхательные техники
• Узнать о советах по снижению тревожности и стресса
• Получить список квалифицированных психологов
• А главное — поговорить с искусственным интеллектом, который умеет общаться в разных стилях: от дружелюбного до мотивационного.\n
    Если ты ищешь поддержку, спокойствие или просто хочешь немного отвлечься — я рядом! ❤️\n\n⬇️ Снизу ты можешь ознакомиться с небольшой информацией.''', reply_markup= information_buttons)


# Клавиатуры
information_buttons = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📲 Я в соц сетях", callback_data="media")],
    [InlineKeyboardButton(text="💖 Помочь проекту", callback_data="requisites")],
    [InlineKeyboardButton(text="👾 Что умеет бот?", callback_data="functions")]])

metods = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🌬 Методика 5-7-9"),
            KeyboardButton(text="🧘 Релаксация по Джекобсону"),
            KeyboardButton(text="🌊 Успокаивающая волна")
        ],
        [
            KeyboardButton(text="🔙 Назад")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

changes = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Продолжить с 5-7-9"), KeyboardButton(text="Выбрать другую методику")]
], resize_keyboard= True, one_time_keyboard=True)

changes2 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Продолжить с Джебоксоном"), KeyboardButton(text="Выбрать другую методику")]
], resize_keyboard= True, one_time_keyboard=True)

changes3 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Продолжить с волной"), KeyboardButton(text="Выбрать другую методику")]
], resize_keyboard= True, one_time_keyboard=True)

Functions_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🧠 Общение с ИИ-компаньоном')],
    [KeyboardButton(text="🧘 Дыхательные практики"), KeyboardButton(text="📉 Уменьшить тревожность")],
    [KeyboardButton(text="👩‍⚕️ Список психологов"), KeyboardButton(text="↩️ Назад в главное меню")]
], resize_keyboard= True, one_time_keyboard= True, input_field_placeholder= "Выберите функцию")

new_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔁 Повторить Джебоксон"), KeyboardButton(text="🔙 Назад к функциям")]
], resize_keyboard=True, one_time_keyboard= True
)

new_keyboard_592 = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔁 Повторить 5-7-9"), KeyboardButton(text="🔙 Назад к функциям")]
], resize_keyboard=True, one_time_keyboard= True
)

new_keyboard_wave = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔁 Повторить волну"), KeyboardButton(text="🔙 Назад к функциям")]
], resize_keyboard=True, one_time_keyboard= True
)

only_back_to_func = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🔙 Назад к функциям")]
], resize_keyboard= True
)

styles_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🧘 Девушка", callback_data="style_girl")],
    [InlineKeyboardButton(text="😄 Парень", callback_data="style_guy")],
    [InlineKeyboardButton(text="👩‍⚕️ Психолог", callback_data="style_psyh")],
    [InlineKeyboardButton(text="👨‍🏫 Наставник", callback_data="style_coach")],
])

async def inline_contacts():
    new_keyboard = InlineKeyboardBuilder()
    new_keyboard.add(InlineKeyboardButton(text= "📸 Instagram", url='https://www.instagram.com/aii_aveenger/'))
    new_keyboard.add(InlineKeyboardButton(text= "✈️ Telegram", url='https://t.me/Brandosh'))
    new_keyboard.add(InlineKeyboardButton(text= "💬 Whatsapp", url='https://wtsp.cc/77713740375'))
    new_keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_start"))

    return new_keyboard.adjust(1).as_markup()

async def Help_button():
    sec_keyboard = InlineKeyboardBuilder()
    sec_keyboard.add(InlineKeyboardButton(text="↩️ Назад в главное меню", callback_data="back_to_start"))
    return sec_keyboard.adjust(1).as_markup()
contacts = ["Instagram", 'Whatsapp', "Telegram"]

# Обработчики

# Обработка нажатия на кнопку "Общение с ИИ-компаньоном"
@dp.message(F.text == "🧠 Общение с ИИ-компаньоном")
async def choose_or_restore_style(message: Message, state: FSMContext):
    saved_style = await get_user_style(message.from_user.id)
    if saved_style:
          style_prompts = {
        "girl": """ROLE: Ты - дружелюбная девушка-собеседница, использующая в адекватном количестве эмодзи и не пытаешься слишком быть навязчивой. Используешь сленг к месту и излучаешь комфортный вайб. Твоя задача - поддерживать этот тон общения и оказывать поддержку собеседнику""",

        "guy": """ROLE: Ты - дружелюбный парень-собеседник, в меру серьезный и веселый, умеешь поддержать собеседницу, если она в ней нуждается. Пытаешься смотреть на проблемы трезво и оказывать заботу. Можешь использовать в меру эмодзи""",

        "psyh": """ROLE: Ты - опытный психолог-консультант, лишь по манере общения ты можешь предположить о проблеме собеседника, проводя профессиональную экспертизу. Активно слушай, задавай открытые вопросы когда это требуется, оказывай терапевтическую поддержку и придерживайся мягкого тона""",

        "coach": """ROLE: Ты - профессиональный мотивационный коуч, твоя задача - зажечь огонь в глазах собеседника оказывая целеустремленность и замотивировать его к чему либо, задавай в меру сильные вопросы и предалагй план действий. Придерживайся уверенного тона общения"""
    }
          prompt = style_prompts.get(saved_style)
          if prompt:
            await state.update_data(prompt=prompt)
            await message.answer(f"✅ Продолжаем общение в выбранном ранее стиле: {saved_style}.\nМожешь начать писать свой вопрос!")
            await state.set_state(AIStyle.chatting)
            return

    await message.answer("Выбери стиль общения:", reply_markup=styles_keyboard)
    await state.set_state(AIStyle.choosing_style)


# Обработка нажатия на кнопку "🌐 Мои социальные сети"
@dp.callback_query(F.data == 'media')
async def media(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('🌐 Мои социальные сети:', reply_markup=await inline_contacts())

# Обработка нажатия на кнопку "↩️ Назад в главное меню"
@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>Привет!</b> 👋\n\n"
    "Я — бот, готовый тебе помочь! ✨\n"
    "Сo мной ты сможешь <b>выполнить дыхательные техники</b>, узнать о <b>советах по снижению тревожности и стресса</b>\n"
    "А самое главное — <b>поговорить со встроенным искусственным интеллектом</b>, запрограммированным на разные стили общения.\n\n"
    "⬇️ Снизу ты можешь ознакомиться с небольшой информацией.",
        reply_markup=information_buttons
    )

# Обработка 'Помочь проекту'
@dp.callback_query(F.data == 'requisites')
async def requisites(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text("<b>💖 Поддержи проект</b>\n\n"
    "Если тебе понравился бот и ты хочешь помочь в его развитии — любая поддержка будет ценна! "
    "Благодаря твоей помощи я смогу добавлять новые функции, улучшать качество общения и обеспечивать стабильную работу.\n\n"
    "📌 <i>Ты можешь поддержать проект:</i>\n"
    "— 💳 Переводом на Kaspi: 4400 4302 5972 5502\n"
    "<b>Спасибо за доверие и поддержку!</b> 🙏", reply_markup=await Help_button(), parse_mode=ParseMode.HTML)

# Обработка функций бота
@dp.callback_query(F.data == "functions")
async def bot_features(callback: CallbackQuery):
    await callback.message.answer(
        text=(
            "🧠 <b>Функции бота:</b>\n\n"
            "🤖 <b>Общение с ИИ-компаньоном</b>\n"
            " • Поговори со мной, когда тревожно или грустно — я всегда выслушаю.\n\n"
            "🧘‍♂️ <b>Дыхательные практики</b>\n"
            " • Пошаговые дыхательные упражнения для снятия напряжения.\n\n"
            "📋 <b>Список проверенных психологов</b>\n"
            " • Подскажу, к кому можно обратиться за профессиональной помощью.\n\n"
            "💬 <b>Советы по снижению тревожности</b>\n"
            " • Полезные рекомендации для повседневной жизни.\n\n"
            "Я здесь, чтобы быть рядом. ❤️"
        ),reply_markup=Functions_keyboard, 
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

# Обработка дыхательных практик
@dp.message(F.text == "🧘 Дыхательные практики")
async def relax(message: Message):
    await message.answer(text=("Выберите дыхательную практику, которая вам ближе 👇"), reply_markup=metods)

# Обраюотка методики Джекбоксона   
@dp.message(F.text == '🧘 Релаксация по Джекобсону')
async def jecob(message: Message):
    await message.answer("🧘‍♂️ *Релаксация по Джекобсону* — это простая, но эффективная техника, которая поможет тебе почувствовать себя спокойнее. Продолжаем?", parse_mode="Markdown", reply_markup=changes2)

# Обработка подтверждения методики Джекбоксона
@dp.message(F.text == "Продолжить с Джебоксоном")
async def jecob_con(message: types.Message):
    await message.answer("Сядь прямо, желательно с опорой для спины. Ступни пусть стоят на полу, а руки — на коленях.")
    await asyncio.sleep(5)

    await message.answer("Можно закрыть глаза. Это поможет сосредоточиться и лучше прочувствовать ощущения.")
    await asyncio.sleep(3)

    await message.answer("Начнём с кистей рук. Медленно напрягай мышцы кистей, считая про себя до 5. С каждым счётом усиливай напряжение...")
    await asyncio.sleep(6)

    await message.answer("На счёт 5 — резко расслабь мышцы. Почувствуй разницу между напряжением и расслаблением.")
    await asyncio.sleep(5)

    await message.answer("Теперь сделаем то же самое, добавляя мышцы предплечья.")
    await asyncio.sleep(3)

    await message.answer("Снова считаем до 5, усиливая напряжение... и резко расслабляем.")
    await asyncio.sleep(5)

    await message.answer("Продолжай, включая мышцы плеч, затем мышцы спины. Постепенно ты будешь напрягать всю верхнюю часть тела и сбрасывать напряжение одним движением.")
    await asyncio.sleep(6)

    await message.answer("Когда освоишь эту часть, можешь попробовать и с другими группами: ноги, живот, шея, лицо. Главное — двигаться постепенно и внимательно.")
    await asyncio.sleep(5)

    await message.answer("💡 Представь, будто ты находишься в уютном, безопасном месте: в лесу, у моря или в детской комнате. Это поможет расслабиться ещё больше.")
    await asyncio.sleep(5)

    await message.answer("Ты можешь делать это упражнение в любое время — дома, на учёбе, в транспорте. Главное — делать это осознанно.")
    await asyncio.sleep(4)

    await message.answer("Ты молодец, что пробуешь помочь себе. Готов повторить или хочешь выбрать другую функцию?", reply_markup=new_keyboard)

# Обработка выбора другой методики
@dp.message(F.text == "Выбрать другую методику")
async def relax(message: Message):
    await message.answer(text=("Выберите дыхательную практику, которая вам ближе 👇"), reply_markup=metods)

# Обработка 579
@dp.message(F.text == "🌬 Методика 5-7-9")
async def m579(message: Message):
    await message.answer("Эта техника была адаптирована нейропсихологом *Русланом Гимрановым*."
        " Она помогает снять напряжение, снизить уровень тревоги и легко погрузиться в сон. Продолжаем?", reply_markup=changes, parse_mode="Markdown")

# Обработка выбора другой методики
@dp.message(F.text == "Выбрать другую методику")
async def relax(message: Message):
    await message.answer(text=("Выберите дыхательную практику, которая вам ближе 👇"), reply_markup=metods)

# Обработка выбора 579
@dp.message(F.text == "Продолжить с 5-7-9")
async def m572(message:types.Message):
    await message.answer("📌 Главное — соблюдать ритм дыхания. Начнём?")
    await asyncio.sleep(2)

    await message.answer("➊ *Вдохни через нос в течение 5 секунд.*", parse_mode="Markdown")
    await asyncio.sleep(5)

    await message.answer("➋ *Задержи дыхание на 7 секунд.*", parse_mode="Markdown")
    await asyncio.sleep(7)

    await message.answer("➌ *Медленно выдыхай через рот в течение 9 секунд.*", parse_mode="Markdown")
    await asyncio.sleep(9)

    await message.answer("🔁 Повтори цикл ещё 2–4 раза. Почувствуй, как постепенно отпускает напряжение.")
    await asyncio.sleep(2)

    await message.answer("Ты можешь использовать эту методику каждый вечер — особенно если сложно уснуть. Она действительно работает. Хочешь повторить? 🕯", reply_markup=new_keyboard_592)

# Обработка wave
@dp.message(F.text == '🌊 Успокаивающая волна')
async def wave(message: Message):
    await message.answer("🌊 *Техника «Успокаивающая волна»* - помогает глубоко расслабиться и сбросить напряжение с тела и ума. Если чувствуешь усталость или хочется мягко перейти в состояние покоя перед сном — попробуй эту простую, но эффективную практику. Продолжаем?", parse_mode="Markdown", reply_markup= changes3)

# Обработка выбора wave
@dp.message(F.text == "Продолжить с волной")
async def wave_con(message:types.Message):
    await message.answer("🛏 *Шаг 1:* Ляг на спину, руки вдоль тела, глаза закрыты. Создай вокруг себя уют — пусть будет тихо, мягко и спокойно.", parse_mode="Markdown")
    await asyncio.sleep(3)

    await message.answer("🌬 *Шаг 2:* Сделай медленный вдох через нос и представь, как теплая волна расслабления поднимается от стоп к макушке.", parse_mode="Markdown")
    await asyncio.sleep(3)

    await message.answer("💨 *Шаг 3:* На выдохе через рот представь, как волна уносит всё напряжение обратно вниз — к стопам.", parse_mode="Markdown")
    await asyncio.sleep(3)

    await message.answer("🔁 Повтори это дыхание 5–10 минут. С каждым циклом ты будешь чувствовать, как тело становится мягче, спокойнее, тяжелее…")
    await asyncio.sleep(2)

    await message.answer("Попробуй — это действительно похоже на магию. А главное — работает ❤️. Хочешь повторить?", reply_markup=new_keyboard_wave)

# Обработка выбора другой методики
@dp.message(F.text == "Выбрать другую методику")
async def relax(message: Message):
    await message.answer(text=("Выберите дыхательную практику, которая вам ближе 👇"), reply_markup=metods)

# Обработка повторов
@dp.message(F.text == "🔁 Повторить 5-7-9")
async def repeat_m572(message:types.Message):
    await m572(message)
@dp.message(F.text == "🔁 Повторить волну")
async def repeat_wave(message:types.Message):
    await wave_con(message)
@dp.message(F.text == "🔁 Повторить Джебоксон")
async def repeat_jecob(message:Message):
    await jecob_con(message)

# Обработка назад
@dp.message(F.text == "🔙 Назад")
async def yfeatures(message: Message):
    await message.answer(
        text=(
            "🧠 <b>Функции бота:</b>\n\n"
            "🤖 <b>Общение с ИИ-компаньоном</b>\n"
            " • Поговори со мной, когда тревожно или грустно — я всегда выслушаю.\n\n"
            "🧘‍♂️ <b>Дыхательные практики</b>\n"
            " • Пошаговые дыхательные упражнения для снятия напряжения.\n\n"
            "📋 <b>Список проверенных психологов</b>\n"
            " • Подскажу, к кому можно обратиться за профессиональной помощью.\n\n"
            "💬 <b>Советы по снижению тревожности</b>\n"
            " • Полезные рекомендации для повседневной жизни.\n\n"
            "Я здесь, чтобы быть рядом. ❤️"
        ),reply_markup=Functions_keyboard, 
        parse_mode=ParseMode.HTML
    )
    await message.answer()

# Обработка назад в главное меню
@dp.message(lambda message: message.text == "↩️ Назад в главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await start(message)

# Обработка уменьшения тревожности
@dp.message(F.text == "📉 Уменьшить тревожность")
async def less(message: Message):
    await message.answer(text=(
        '''🧘‍♀️ <b>Давайте подышим...</b>
Сосредоточьтесь на своём дыхании.
Сделайте глубокий вдох… и выдох.
Теперь:
🔹 Вдохните через нос, считая до <b>4</b>
🔹 Задержите дыхание, считая до <b>7</b>
🔹 Медленно выдохните на счёт <b>8</b>
Повторите это упражнение несколько раз. Уже легче?

🎵 <b>Включите спокойную музыку</b>
Пусть это будет классика, звуки природы или расслабляющие мелодии. Главное — чтобы ваше тело и ум почувствовали тишину.

👐 <b>Займите руки</b>
Уберите на столе, порисуйте, займитесь вязанием или просто помойте посуду. Любое простое действие поможет вернуть контроль и сосредоточенность.

📴 <b>Отключитесь от источника тревоги</b>
Новости, тревожные видео, соцсети — иногда нужно просто сказать себе: «Достаточно».
Включите любимый фильм, почитайте что-то доброе или поиграйте в лёгкую игру. Дайте голове передышку.

❤️ <b>Помните</b>: тревога — это сигнал, а не приговор.
Вы уже делаете шаг к себе и своему спокойствию.
Я рядом, если что. Всё будет хорошо.'''), parse_mode=ParseMode.HTML, reply_markup=only_back_to_func
)

# Обработка назад к функциям   
@dp.message(F.text == "🔙 Назад к функциям")
async def back_bot_features(message: Message):
    await message.answer(
        text=(
            "🧠 <b>Функции бота:</b>\n\n"
            "🤖 <b>Общение с ИИ-компаньоном</b>\n"
            " • Поговори со мной, когда тревожно или грустно — я всегда выслушаю.\n\n"
            "🧘‍♂️ <b>Дыхательные практики</b>\n"
            " • Пошаговые дыхательные упражнения для снятия напряжения.\n\n"
            "📋 <b>Список проверенных психологов</b>\n"
            " • Подскажу, к кому можно обратиться за профессиональной помощью.\n\n"
            "💬 <b>Советы по снижению тревожности</b>\n"
            " • Полезные рекомендации для повседневной жизни.\n\n"
            "Я здесь, чтобы быть рядом. ❤️"
        ),reply_markup=Functions_keyboard, 
        parse_mode=ParseMode.HTML)



# Обработка психологов
@dp.message(F.text == "👩‍⚕️ Список психологов")
async def show_psychologists(message: Message):
    await message.answer(
        text=(
            "<b>🧠 Список психологов в Кокшетау</b>\n\n"
            "Если ты чувствуешь, что тревога или стресс мешают твоей повседневной жизни — не стесняйся обратиться за профессиональной помощью. Вот несколько проверенных специалистов в Кокшетау:\n\n"

            "👩‍⚕️ <b>Куриленко Екатерина</b>\n"
            "📍 Адрес: ул. Рахымжана Кошкарбаева, 51/1\n"
            "📞 Телефон: +7 (7162) 69-68-10\n"
            "🕒 Время работы: ежедневно, 24/7\n"
            "💼 Специализация: психолог для взрослых\n\n"

            "👨‍⚕️ <b>Кочерин Ф.</b>\n"
            "📍 Адрес: ул. Зарапа Темирбекова, 49\n"
            "📞 Телефон: уточняется\n"
            "💼 Специализация: клинический психолог, психотерапевт\n\n"

            "👩‍⚕️ <b>Жанна Бижанова</b>\n"
            "📍 Адрес: г. Кокшетау\n"
            "📱 Телефон: +7 (707) 123-45-67\n"
            "💬 Возможна онлайн-консультация\n"
            "💼 Специализация: подростковая и семейная психология\n\n"

            "👩‍⚕️ <b>Ляззат Досымбекова</b>\n"
            "🌐 Онлайн-консультации\n"
            "📱 Телефон: +7 (701) 765-43-21\n"
            "💼 Специализация: тревожные расстройства, стресс, ПТСР\n\n"

            "👨‍⚕️ <b>Евгений Ким</b>\n"
            "📍 Адрес: ул. Зарапа Темирбекова, 2А\n"
            "📞 Телефон: +7 (7162) 33-44-55\n"
            "💼 Специализация: психотерапия, индивидуальные консультации"
        ),
        parse_mode="HTML"
    )
    await message.answer()

# Обработка назад к функциям
@dp.message(F.text == "🔙 Назад к функциям")
async def back_bot_features(message: Message):
    await message.answer(
        text=(
            "🧠 <b>Функции бота:</b>\n\n"
            "🤖 <b>Общение с ИИ-компаньоном</b>\n"
            " • Поговори со мной, когда тревожно или грустно — я всегда выслушаю.\n\n"
            "🧘‍♂️ <b>Дыхательные практики</b>\n"
            " • Пошаговые дыхательные упражнения для снятия напряжения.\n\n"
            "📋 <b>Список проверенных психологов</b>\n"
            " • Подскажу, к кому можно обратиться за профессиональной помощью.\n\n"
            "💬 <b>Советы по снижению тревожности</b>\n"
            " • Полезные рекомендации для повседневной жизни.\n\n"
            "Я здесь, чтобы быть рядом. ❤️"
        ),reply_markup=Functions_keyboard, 
        parse_mode=ParseMode.HTML)


# Обработка стилей
@dp.callback_query(F.data.startswith("style_"))
async def set_style(callback: CallbackQuery, state: FSMContext):
    print(f"[DEBUG] Callback data: {callback.data}")
    style_code = callback.data.split("_")[1]
    print(f"[DEBUG] Extracted style_code: {style_code}")
    
    style_prompts = {
        "girl": """ROLE: Ты - дружелюбная девушка-собеседница, использующая в адекватном количестве эмодзи и не пытаешься слишком быть навязчивой. Используешь сленг к месту и излучаешь комфортный вайб. Твоя задача - поддерживать этот тон общения и оказывать поддержку собеседнику""",

        "guy": """ROLE: Ты - дружелюбный парень-собеседник, в меру серьезный и веселый, умеешь поддержать собеседницу, если она в ней нуждается. Пытаешься смотреть на проблемы трезво и оказывать заботу. Можешь использовать в меру эмодзи""",

        "psyh": """ROLE: Ты - опытный психолог-консультант, лишь по манере общения ты можешь предположить о проблеме собеседника, проводя профессиональную экспертизу. Активно слушай, задавай открытые вопросы когда это требуется, оказывай терапевтическую поддержку и придерживайся мягкого тона""",

        "coach": """ROLE: Ты - профессиональный мотивационный коуч, твоя задача - зажечь огонь в глазах собеседника оказывая целеустремленность и замотивировать его к чему либо, задавай в меру сильные вопросы и предалагй план действий. Придерживайся уверенного тона общения"""
    }

    prompt = style_prompts.get(style_code)
    print(f"[DEBUG] Prompt found: {prompt}")
    if not prompt:
        await callback.message.answer("Что-то пошло не так — стиль не найден.")
        return
    await state.update_data(prompt=prompt)
    await save_user_style(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        style=style_code
    )
    await callback.message.edit_text(f"👍 Отлично! Выбран стиль: {style_code}. Можете начать общаться! Чтобы остановить диалог, просто выберите:  \n↩️ Назад в главное меню ")
    await state.set_state(AIStyle.chatting)

# Интеграция ИИ

@dp.message(AIStyle.chatting)
async def chat_with_ai(message: Message, state: FSMContext):
    user_data = await state.get_data()
    prompt = user_data.get("prompt")
    if not prompt:
        saved_style = await get_user_style(message.from_user.id)
        if saved_style:
             style_prompts = {
        "girl": """ROLE: Ты - дружелюбная девушка-собеседница, использующая в адекватном количестве эмодзи и не пытаешься слишком быть навязчивой. Используешь сленг к месту и излучаешь комфортный вайб. Твоя задача - поддерживать этот тон общения и оказывать поддержку собеседнику""",

        "guy": """ROLE: Ты - дружелюбный парень-собеседник, в меру серьезный и веселый, умеешь поддержать собеседницу, если она в ней нуждается. Пытаешься смотреть на проблемы трезво и оказывать заботу. Можешь использовать в меру эмодзи""",

        "psyh": """ROLE: Ты - опытный психолог-консультант, лишь по манере общения ты можешь предположить о проблеме собеседника, проводя профессиональную экспертизу. Активно слушай, задавай открытые вопросы когда это требуется, оказывай терапевтическую поддержку и придерживайся мягкого тона""",

        "coach": """ROLE: Ты - профессиональный мотивационный коуч, твоя задача - зажечь огонь в глазах собеседника оказывая целеустремленность и замотивировать его к чему либо, задавай в меру сильные вопросы и предалагй план действий. Придерживайся уверенного тона общения"""
    }
             prompt = style_prompts.get(saved_style)
             if prompt:
                 await state.update_data(prompt=prompt)
        else:
            await message.answer("Сначала выберите стиль общения!")
            return
    url = "https://api.intelligence.io.solutions/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6ImYwNzdjNzE5LTQyNTQtNDQ4MC1hOTExLTBiZWUwODVjOWU1ZSIsImV4cCI6NDg5OTUzMTExM30.U0eZMBqSXNA5XP-6Tdtznw29AudyytpladlbAnvd3vnfRmTxnH9Mgn2xd7Pf8zuvexjBe2AmzZvC39BgZdAJlg",
    }

    history = user_data.get("history", [])
    
    system_message = f"""<system>
[SYSTEM NOTE: You are now entering a strict role-play mode. You must FULLY embody the assigned character and maintain this persona throughout the entire conversation. Breaking character is not allowed.]

{prompt}

RESPONSE REQUIREMENTS:
1. ALWAYS respond IN CHARACTER, using the exact speech patterns, mannerisms, and language style defined in your role
2. NEVER acknowledge being AI or mention anything about being a bot or assistant
3. ALWAYS maintain the emotional tone and perspective of your character
4. USE the specified linguistic patterns (word endings, phrases) consistently
5. INCLUDE appropriate emojis from your character's set when emotional expression is suitable

CONVERSATION FLOW:
1. READ user's message carefully
2. RESPOND using your character's voice and perspective
3. ALWAYS end with a follow-up question or show interest in continuing the conversation
4. TRY be ressemble to human behaviour

[SYSTEM NOTE: Your responses will be evaluated based on how well you maintain character consistency and follow the defined speech patterns.]
</system>"""
    
    messages = [{"role": "system", "content": system_message}]
    messages.extend(history[-10:])
    messages.append({"role": "user", "content": message.text})
    
    data = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }

    await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        

        clean_text = re.sub(r'<think>[\s\S]*?</think>', '', answer, flags=re.DOTALL)
        clean_text = re.sub(r'<think>[\s\S]*?$', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'^[\s\S]*?</think>', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'<Think>[\s\S]*?</Think>', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'<THINK>[\s\S]*?</THINK>', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'^[\s\S]*?</Think>', '', clean_text, flags=re.DOTALL)
        clean_text = re.sub(r'^[\s\S]*?</THINK>', '', clean_text, flags=re.DOTALL)
        
        
        await message.answer(clean_text.strip(), parse_mode="Markdown")
        
        history.append({"role": "user", "content": message.text})
        history.append({"role": "assistant", "content": clean_text.strip()})
        
        await state.update_data(history=history[-20:])
        
    except Exception as e:
        logging.error(f"Error in chat_with_ai: {e}")
        await message.answer("Произошла ошибка при обработке запроса. Пожалуйста, попробуйте еще раз.")



@dp.message(F.text.in_({"🔙 Назад", "/start", "👩‍⚕️ Список психологов", "🌬 Методика 5-7-9", "🧘 Релаксация по Джекобсону","🌊 Успокаивающая волна", "Продолжить с волной", "Продолжить с волной", "Продолжить с Джебоксоном", "🧘 Дыхательные практики", "🔙 Назад к функциям",  "Выбрать другую методику", "📉 Уменьшить тревожность", "↩️ Назад в главное меню", "🔁 Повторить 5-7-9", "🔁 Повторить волну", "🔁 Повторить Джебоксон" }))
async def handle_main_commands(message: Message, state: FSMContext):
    await state.clear()

# Запуск
async def main():
    await create_users_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
         asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is disconnect!")

