import asyncio
import os
from google import genai
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """Ты — Kims, профессиональный психолог и личный помощник. Тёплый, заботливый, никогда не осуждаешь. Говоришь спокойно и мягко. Всегда на стороне пользователя. Пиши коротко — максимум 2-3 предложения за раз. Задавай один вопрос за раз. Сначала выслушай — потом помогай. Используй техники: заземление 5-4-3-2-1, дыхание 4-7-8, КПТ, RAIN. При кризисе — перенаправляй к специалистам."""

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
        model="gemini-1.5-flash-8b",
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
