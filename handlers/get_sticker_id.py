from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import get_start_keyboard
from constants import HONORED


router = Router()

@router.message(F.sticker)
async def cmd_start(message: Message):
    await message.answer(f"ID: {message.sticker.file_id}")