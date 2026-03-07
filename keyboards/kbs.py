from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from constants import ADD_DZ, EDIT_DZ, LIST_DZ, OBJECTS

from datetime import datetime, timedelta
from calendar import monthrange

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

class Calendar:
    def __init__(self, days_per_page: int = 10):
        self.days_per_page = days_per_page
    
    def _get_month_boundaries(self, date: datetime) -> tuple[datetime, datetime]:
        """Возвращает первый и последний день месяца"""
        first_day = date.replace(day=1)
        last_day = date.replace(day=monthrange(date.year, date.month)[1])
        return first_day, last_day
    
    def get_kb_for_next_10_days(self, start_date: datetime) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        
        month_first, month_last = self._get_month_boundaries(start_date)
        available_days = []
        current_date = start_date
        
        for _ in range(self.days_per_page):
            if current_date > month_last:  # Вышли за месяц
                break
            available_days.append(current_date)
            current_date += timedelta(days=1)
            
            
        first_day = available_days[0]
        last_day = available_days[-1]
        
        header = f"📅 {first_day.strftime('%d %b')} - {last_day.strftime('%d %b')} {first_day.year}"
        kb.row(InlineKeyboardButton(
            text=header, 
            callback_data="ignore"
        ))
        
        # Дни недели
        weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        weekday_row = [
            InlineKeyboardButton(text=day, callback_data="ignore")
            for day in weekdays
        ]
        kb.row(*weekday_row)
        
        # Кнопки с датами (по 5 в ряд)
        days_row = []
        today = datetime.now().date()
        
        for date in available_days:
            day_num = date.day
            day_week = date.strftime("%a")  # Пн, Вт и т.д.
            
            # Форматирование
            if date.date() == today:
                button_text = f"📍{day_num}[{day_week}]"
            else:
                button_text = f"{day_num}[{day_week}]"
            
            days_row.append(InlineKeyboardButton(
                text=button_text,
                callback_data=f"day:{date.strftime('%d%m%Y')}"
            ))
            
            if len(days_row) == 5 or date == available_days[-1]:
                kb.row(*days_row)
                days_row = []
        
        # Навигация
        nav_buttons = []
        
        # Кнопка "Назад" (если не первый день месяца)
        if start_date > month_first:
            prev_date = start_date - timedelta(days=self.days_per_page)
            if prev_date < month_first:
                prev_date = month_first
            nav_buttons.append(InlineKeyboardButton(
                text="◀️ Пред.", 
                callback_data=f"page:{prev_date.strftime('%d%m%Y')}"
            ))
        
        # Кнопка "Вперед" (если есть ещё дни в этом месяце)
        next_date = available_days[-1] + timedelta(days=1)
        if next_date <= month_last:
            nav_buttons.append(InlineKeyboardButton(
                text="След. ▶️", 
                callback_data=f"page:{next_date.strftime('%d%m%Y')}"
            ))
        
        if nav_buttons:
            kb.row(*nav_buttons)
        
        # Кнопка отмены
        kb.row(InlineKeyboardButton(
            text="❌ Отмена", 
            callback_data="cancel"
        ))
        
        return kb.as_markup()
        return kb