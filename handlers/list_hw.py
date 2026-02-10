from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

from constants import MAIN_MENU_TEXT, OBJECTS, LIST_DZ, LIST_HW_TEXT
from database import get_active_hws, get_hw_by_id
from keyboards import get_kb_for_hws_with_files
from .somecoolshit import days_until_deadline

router = Router()

@router.message(F.text == LIST_DZ)
async def add_hw_init(message: Message):
    hws = get_active_hws()
    # Инициализируем пустые данные
    #hws_data = {
    #    "object": hws[1],
    #    "description": hws[2],
    #    "files": len(eval(hws[3])),
    #    "created_at": hws[4],
    #    "ends_at": hws[5],
    #    "menu_msg_id": callback.message.message_id
    #}
    text = "Для просмотра файлов нажми на кнопку с соответствующим ID\n"
    ids_of_hws_with_files = []
    
    for hw in hws:
        text = text + LIST_HW_TEXT.format(hw[1].capitalize(), hw[0], len(eval(hw[3])),hw[2], hw[4], hw[5], days_until_deadline(hw[5]))
        if len(eval(hw[3])) > 0:
            ids_of_hws_with_files.append(hw[0])
    
    await message.bot.send_message(message.from_user.id, text, reply_markup=get_kb_for_hws_with_files(ids_of_hws_with_files), parse_mode="MarkdownV2")

@router.callback_query(F.data.startswith("list_hw:"))
async def extended_hw_info(callback: CallbackQuery):
    hw = get_hw_by_id(callback.data[8:])
    text = LIST_HW_TEXT.format(hw[1].capitalize(), hw[0], len(eval(hw[3])),hw[2], hw[4], hw[5], days_until_deadline(hw[5]))
    
    await callback.bot.send_message(callback.from_user.id, text, parse_mode="MarkdownV2")
    
    for file_id in eval(hw[3]):
        await send_unknown_file(callback.bot, callback.from_user.id, file_id)

async def send_unknown_file(bot: Bot, chat_id: int, file_id: str):
    """
    Пытаемся отправить неизвестный файл как документ
    Работает для большинства типов
    """
    try:
        await bot.send_document(
            chat_id=chat_id,
            document=file_id,
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        await handle_unknown_type(bot, chat_id, file_id, e)

async def handle_unknown_type(bot: Bot, chat_id: int, file_id: str, error=None):
    """Попробуем все возможные типы"""
    
    methods = [
        ("photo", bot.send_photo),
        ("video", bot.send_video),
        ("audio", bot.send_audio),
        ("voice", bot.send_voice),
        ("animation", bot.send_animation),
        ("sticker", bot.send_sticker),
        ("video_note", bot.send_video_note),
    ]
    
    for file_type, method in methods:
        try:
            if file_type in ["photo", "video", "animation"]:
                await method(chat_id, file_id)
            else:
                await method(chat_id, file_id)
            return True
        except:
            continue
        
    await bot.send_message(chat_id, "❌ Не удалось отправить файл")
    return False