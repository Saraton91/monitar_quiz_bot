import json
import random
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Загружаем вопросы
with open("final_moliya_test.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

user_states = {}

@dp.message(CommandStart())
async def start(message: types.Message):
    await send_question(message.chat.id)

async def send_question(chat_id):
    question = random.choice(questions)
    user_states[chat_id] = question
    variants_text = ""
    for i, option in enumerate(question["options"]):
        variants_text += f"{chr(65+i)}) {option}\n"
    
    text = f"<b>❓ Savol:</b>\n{question['question']}\n\n{variants_text}"
    
    builder = InlineKeyboardBuilder()
    for i in range(len(question["options"])):
        builder.button(text=chr(65+i), callback_data=str(i))
    builder.adjust(2)
    
    await bot.send_message(chat_id, text, reply_markup=builder.as_markup())

@dp.callback_query(F.data)
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    selected_index = int(callback.data)
    question = user_states.get(user_id)

    if question:
        correct_index = question["correct_option_index"]
        selected_text = question["options"][selected_index]
        correct_text = question["options"][correct_index]
        
        if selected_index == correct_index:
            response = f"✅ <b>To‘g‘ri javob!</b>\n\n<i>{chr(65+selected_index)}) {selected_text}</i>"
        else:
            response = (
                f"❌ <b>Noto‘g‘ri</b>\n\n"
                f"<b>Siz tanlagan javob:</b> {chr(65+selected_index)}) {selected_text}\n"
                f"<b>To‘g‘ri javob:</b> {chr(65+correct_index)}) {correct_text}"
            )
        await callback.answer()
        await bot.send_message(user_id, response)
        await send_question(user_id)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
