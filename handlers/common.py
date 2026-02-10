from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()

@router.message(Command("zzz"))
async def cmd_start(message: types.Message):
    if message.from_user.id != 1246001753:
        await message.answer("Ты не кирилл сорян")
        return 1

    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Основное меню"))
    
    await message.answer(
        "Выбери действие:",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

# Пример обработки текста с кнопки (Magic Filter - F)
@router.message(F.text == "Kupit' anashu")
async def info_handler(message: types.Message):
    text = (
        "a hui tebe"
    )
    # Удаляем клавиатуру после нажатия (для примера)
    await message.answer(text, parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
