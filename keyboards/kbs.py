from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from constants import ADD_DZ, EDIT_DZ, LIST_DZ, OBJECTS

def get_start_keyboard():
    """Клавиатура с одной кнопкой"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ADD_DZ)],
            [KeyboardButton(text=EDIT_DZ)],
            [KeyboardButton(text=LIST_DZ)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard

def get_dif_start_keyboard():
    """Клавиатура с одной кнопкой"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LIST_DZ)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    return keyboard

def get_add_hw_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📒 Предмет", callback_data="add_hw:object")
    kb.button(text="🗒️ Описание", callback_data="add_hw:description")
    kb.button(text="⏲️ Дата начала", callback_data="add_hw:startdate")
    kb.button(text="⏰ Дата конца", callback_data="add_hw:enddate")
    kb.button(text="📂 Файлы", callback_data="add_hw:files")
    kb.button(text="✅ Сохранить", callback_data="add_hw:save")
    kb.adjust(2, 2, 1, 1)
    return kb.as_markup()

def get_kb_for_hws_with_files(ids: list[int]):
    kb = InlineKeyboardBuilder()
    for id in ids:
        kb.button(text=str(id), callback_data=f"list_hw:{id}")
    return kb.as_markup()

def get_objects_kb():
    kb = InlineKeyboardBuilder()
    for obj in OBJECTS:
        kb.button(text=obj.capitalize(), callback_data=f"set_obj:{obj}")
    kb.adjust(3)
    return kb.as_markup()