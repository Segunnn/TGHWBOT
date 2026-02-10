from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import get_start_keyboard, get_dif_start_keyboard
from constants import HONORED


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.from_user.id not in HONORED:
        await message.answer_sticker("CAACAgIAAxkBAAIBIGmI1GM2gEO4molcgyFPYoDqyLkGAALZfAACrSQQSGVM8pLo-wTyOgQ", disable_notification=True)
        await message.answer("Для просмотра актуальных дз жми на кнопочку", reply_markup=get_dif_start_keyboard())
        print(message.from_user.username, message.from_user.id)
        return 0
    text = "Вечер в хату, выбирай действие"
    await message.answer_sticker("CAACAgIAAxkBAAPHaYD04iC0O3lBzzDKsurYwDteWIMAAtNdAAJUWkFIMBqFwQkFyrA4BA", disable_notification=True)
    await message.answer(text, reply_markup=get_start_keyboard())