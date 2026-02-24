from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

from datetime import datetime

from constants import MAIN_MENU_TEXT, OBJECTS, ADD_DZ
from database import validate_date, add_hw
from keyboards import get_add_hw_kb, get_objects_kb

# Состояния
class HWStates(StatesGroup):
    waiting_for_description = State()
    waiting_for_startdate = State()
    waiting_for_enddate = State()
    waiting_for_files = State()

router = Router()

async def update_menu_text(event, state: FSMContext):
    """Вспомогательная функция для обновления текста меню"""
    data = await state.get_data()
    menu_msg_id = data.get("menu_msg_id")
    
    # Берем данные из state или ставим "Не установлено"
    obj = data.get("object", "Не установлено")
    desc = data.get("description", "Не установлено")
    files = data.get("files", [])
    c_at = data.get("created_at", "Не установлено")
    e_at = data.get("ends_at", "Не установлено")

    text = MAIN_MENU_TEXT.format(obj, desc, len(files), c_at, e_at)
    
    await event.bot.edit_message_text(
        chat_id=event.from_user.id, # или event.chat.id, если это Message
        message_id=menu_msg_id,
        text=text,
        reply_markup=get_add_hw_kb(),
        parse_mode="MarkdownV2"
    )

@router.message(F.text == ADD_DZ)
async def add_hw_init(message: Message, state: FSMContext):
    # Инициализируем пустые данные
    msg = await message.bot.send_message(message.chat.id, "Loading...")
    await state.set_data({
        "object": "Не установлено",
        "description": "Не установлено",
        "files": [],
        "created_at": "Не установлено",
        "ends_at": "Не установлено",
        "menu_msg_id": msg.message_id
    })
    await update_menu_text(message, state)

# -------------- СОХРАНЕНИЕ ----------------------
@router.callback_query(F.data == "add_hw:save")
async def save_hw(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    add_hw(data.get('object'), data.get('description'), data.get("files"), data.get("created_at"), data.get("ends_at"))
    await callback.message.delete()
    await callback.answer("✅ Дз сохранено!")

# -------------- ВЫБОР ПРЕДМЕТА--------------------

@router.callback_query(F.data == "add_hw:object")
async def choose_object(callback: CallbackQuery):
    kb = get_objects_kb()
    await callback.message.edit_text("Выберите предмет:", reply_markup=kb)

@router.callback_query(F.data.startswith("set_obj:"))
async def set_object(callback: CallbackQuery, state: FSMContext):
    obj_name = callback.data.split(":")[1]
    await state.update_data(object=obj_name)
    await update_menu_text(callback, state)

# ------------- ОПИСАНИЕ -------------

@router.callback_query(F.data == "add_hw:description")
async def ask_description(callback: CallbackQuery, state: FSMContext):
    await state.set_state(HWStates.waiting_for_description)
    await callback.answer("Введите описание в следующем сообщении")

@router.message(HWStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.delete() 
    await update_menu_text(message, state)
    await state.set_state(None) 

# ------------ ДАТА НАЧАЛА ----------------

@router.callback_query(F.data == "add_hw:startdate")
async def ask_startdate(callback: CallbackQuery, state: FSMContext):
    await state.set_state(HWStates.waiting_for_startdate)
    #await callback.answer("Когда задание было задано? Формат: 11.09.01(день.месяц.год)")
    kb = InlineKeyboardBuilder()
    kb.button(text="Сегодня", callback_data="add_hw:startdate:today")
    msg = await callback.bot.send_message(callback.from_user.id, "Когда дз было задано? Формат: 11.09.01(день.месяц.год) Либо undefined если хз", reply_markup=kb.as_markup())
    await state.update_data(info_msg_id=msg.message_id)

@router.callback_query(F.data == "add_hw:startdate:today")
async def today_startday(callback: CallbackQuery, state: FSMContext):
    await state.update_data(created_at=str(datetime.now().strftime("%d.%m.%y")))
    await callback.bot.delete_message(callback.from_user.id, await state.get_value("info_msg_id"))
    await update_menu_text(callback, state)
    await state.set_state(None)

@router.message(HWStates.waiting_for_startdate)
async def process_startdate(message: Message, state: FSMContext):
    if validate_date(message.text):
        await state.update_data(created_at=message.text)
        await message.delete()
        await message.bot.delete_message(message.from_user.id, await state.get_value("info_msg_id"))
        await update_menu_text(message, state)
        await state.set_state(None)
    else:
        temp_msg = await message.answer("❌ НЕПРАВИЛЬНЫЙ ФОРМАТ. Попробуйте снова")
        await message.delete()
        await message.bot.delete_message(message.from_user.id, await state.get_value("info_msg_id"))
        await state.set_state(None)
        await asyncio.sleep(1)
        await temp_msg.delete()

# ------------ ДАТА КОНЦА ---------------

@router.callback_query(F.data == "add_hw:enddate")
async def ask_startdate(callback: CallbackQuery, state: FSMContext):
    await state.set_state(HWStates.waiting_for_enddate)
    #await callback.answer("Дедлайн до? Формат: 11.09.01(день.месяц.год)")
    msg = await callback.bot.send_message(callback.from_user.id, "Дедлайн до? Формат: 11.09.01(день.месяц.год) Либо undefined если хз")
    await state.update_data(info_msg_id=msg.message_id)

@router.message(HWStates.waiting_for_enddate)
async def process_startdate(message: Message, state: FSMContext):
    if validate_date(message.text):
        await state.update_data(ends_at=message.text)
        await message.delete()
        await update_menu_text(message, state)
        await state.set_state(None)
        await message.bot.delete_message(message.from_user.id, await state.get_value("info_msg_id"))
    else:
        await message.bot.delete_message(message.from_user.id, await state.get_value("info_msg_id"))
        temp_msg = await message.answer("❌ НЕПРАВИЛЬНЫЙ ФОРМАТ. Попробуйте снова")
        await message.delete()
        await state.set_state(None)
        await asyncio.sleep(1)
        await temp_msg.delete()

# ----------- ФАЙЛЫ ----------------

# 1. Вызов режима добавления файлов
@router.callback_query(F.data == "add_hw:files")
async def ask_files(callback: CallbackQuery, state: FSMContext):
    await state.set_state(HWStates.waiting_for_files)
    
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Я загрузил все файлы", callback_data="stop_files")
    
    await callback.message.answer(
        "Присылайте файлы (фото или документы) по одному или пачкой. "
        "Когда закончите, нажмите кнопку ниже.",
        reply_markup=kb.as_markup()
    )

# 2. Ловим файлы (фото и документы)
@router.message(HWStates.waiting_for_files, F.media_group_id)
async def handle_albums(message: Message, state: FSMContext):
    """Обработка альбомов (пачек файлов)"""
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    data = await state.get_data()
    files = data.get("files", [])
    files.append(file_id)
    
    msg_ids = data.get("user_file_msg_ids", [])
    msg_ids.append(message.message_id)
    
    await state.update_data(files=files, user_file_msg_ids=msg_ids)

@router.message(HWStates.waiting_for_files, F.photo | F.document)
async def handle_single_file(message: Message, state: FSMContext):
    """Обработка одиночных файлов"""
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id
    data = await state.get_data()
    files = data.get("files", [])
    files.append(file_id)
    
    msg_ids = data.get("user_file_msg_ids", [])
    msg_ids.append(message.message_id)
    
    await state.update_data(files=files, user_file_msg_ids=msg_ids)

# 3. Выход из режима загрузки
@router.callback_query(F.data == "stop_files")
async def stop_files(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_ids = data.get("user_file_msg_ids", [])
    
    for msg_id in msg_ids:
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id,)
        except Exception as e:
            print(e)
        
    await state.set_state(None)
    await callback.message.delete() # Удаляем инструкцию "Пришлите файлы"
    await state.update_data(user_file_msg_ids=[])
    await update_menu_text(callback, state) # Возвращаемся в главное меню
