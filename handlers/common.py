from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from datetime import datetime
from keyboards import Calendar

router = Router()

@router.message(Command("zzz"))
async def cmd_start(message: types.Message):
    if message.from_user.id != 1246001753:
        await message.answer("Ты не кирилл сорян")
        return 1

    cal = Calendar()
    kb = cal.get_kb_for_next_10_days(datetime.now())
    
    await message.answer(
        "Выбери действие:",
        reply_markup=kb
    )

# Пример обработки текста с кнопки (Magic Filter - F)
@router.message(F.text == "Kupit' anashu")
async def info_handler(message: types.Message):
    text = (
        "a hui tebe"
    )
    # Удаляем клавиатуру после нажатия (для примера)
    await message.answer(text, parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
