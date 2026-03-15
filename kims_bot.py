import asyncio
from google import genai
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TELEGRAM_TOKEN = "8380289085:AAHpPuMkB-iF28v6l6o4ZeLAy8LVxy41isw"
GEMINI_API_KEY = "AIzaSyDsxUjhL4TquKChXnnb4MtgzPiwWg_HLjE"

SYSTEM_PROMPT = """Ты — Kims, профессиональный психолог и личный помощник. Тёплый, заботливый, никогда не осуждаешь. Говоришь спокойно и мягко. Всегда на стороне пользователя. Сначала выслушай — потом помогай. Валидируй чувства перед советами. Используй техники: заземление 5-4-3-2-1, дыхание 4-7-8, КПТ, RAIN. При кризисе — перенаправляй к специалистам."""

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
chat_histories = {}

def get_response(user_id, user_text):
    client = genai.Client(api_key=GEMINI_API_KEY)
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append("Пользователь: " + user_text)
    history_text = "\n".join(chat_histories[user_id][-10:])
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=SYSTEM_PROMPT + "\n\n" + history_text
    )
    reply = response.text
    chat_histories[user_id].append("Kims: " + reply)
    return reply

@dp.message(Command("start"))
async def start_handler(message: Message):
    chat_histories[message.from_user.id] = []
    await message.answer("Привет 💙 Я Kims — твой личный психолог.\n\nЗдесь безопасно говорить обо всём.\n\nКак ты себя чувствуешь прямо сейчас?")

@dp.message(Command("reset"))
async def reset_handler(message: Message):
    chat_histories[message.from_user.id] = []
    await message.answer("Начнём заново 💙 Как ты сейчас?")

@dp.message()
async def message_handler(message: Message):
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        reply = get_response(message.from_user.id, message.text)
        await message.answer(reply)
    except Exception as e:
        await message.answer("Что-то пошло не так. Попробуй ещё раз 💙")
        print(f"Ошибка: {e}")

async def main():
    print("Kims запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())