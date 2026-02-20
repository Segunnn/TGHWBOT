import sqlite3
import json
import os
from pathlib import Path

#from ..constants import OBJECTS
OBJECTS = ("физра", "русский", "физика", "математика", "литература", "химия", "английский", "история", "информатика", "биология", "обществознание", "география", "обзр", "другое")

conn = sqlite3.connect('database/hws.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS hws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object TEXT NOT NULL,
    description TEXT,
    files TEXT,
    created_at TEXT,
    ends_at TEXT,
    status TEXT
)
''')

def validate_object(object: str) -> bool:
    return object.lower().strip() in OBJECTS

def validate_date(date: str) -> bool:
    return ((len(date) == 8) and (date[0].isdigit() and date[1].isdigit() and date[2] == '.' \
            and date[3].isdigit() and date[4].isdigit() and date[5] == '.' \
                and date[6].isdigit() and date[7].isdigit())) or date == "undefined"

def add_hw(object: str, description: str | None, files: list[str] | tuple[str], start_date: str, end_date: str) -> bool:
    """
    object: str - Предмет
    description: str - Суть задания
    files: list[str] - Имена файлов
    start_date: str - Дата начала в виде DD.MM.YY
    end_date: str - Дата окончания в виде DD.MM.YY
    """
    if validate_object(object):
        cur.execute("INSERT INTO hws VALUES (NULL, ?, ?, ?, ?, ?, ?)", (object, description, str(files), start_date, end_date, "active"))
        conn.commit()
    else:
        return False
    return True

def get_active_hws() -> list[tuple[str]]:
    """Returns: 
     [('id', 'object', 'description', "['file_id', ...]", 'start_date', 'end_date', 'status'), (...)]"""
    cur.execute("SELECT * FROM hws WHERE status= 'active'")
    hws = cur.fetchall()
    return hws

def get_outdated_hws():
    cur.execute("SELECT * FROM hws WHERE status='outdated'")
    hws = cur.fetchall()
    return hws

def update_hw(*, hw_id: int, description: str = None, 
            files: list[str] | tuple[str] = None, end_date: str = None, status: str = None) -> bool:
    """
    Обновить домашнее задание по ID
    Возвращает True при успехе, False по настроению
    """
    try:
        updates = []
        params = []
        
        if description:
            updates.append("description = ?")
            params.append(description)
        
        if files:
            updates.append("files = ?")
            params.append(str(files))
        
        if end_date:
            updates.append("ends_at = ?")
            params.append(end_date)
        
        if status:
            updates.append("status = ?")
            params.append(status)
        
        if not updates:
            return False  
        
        params.append(hw_id)
        
        query = f"UPDATE hws SET {', '.join(updates)} WHERE id = ?"
        cur.execute(query, params)
        conn.commit()
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении задания {hw_id}: {e}")
        return False

def delete_hw(hw_id: int) -> bool:
    """
    Удалить домашнее задание по ID
    Возвращает True при успехе, False при ошибке
    """
    try:
        cur.execute("DELETE FROM hws WHERE id = ?", (hw_id,))
        conn.commit()
        return cur.rowcount > 0  
    except Exception as e:
        print(f"Ошибка при удалении задания {hw_id}: {e}")
        return False

def mark_as_outdated(hw_id: int) -> bool:
    """
    Пометить задание как устаревшее (статус 'outdated')
    """
    return update_hw(hw_id=hw_id, status="outdated")

def get_hw_by_id(hw_id: int) -> tuple[int, str, str, str, str, str, str]:
    """
    Returns:
     (id, 'object', 'description', "['fileid', '...']", '00.00.00', '00.00.00', 'status')
    """
    cur.execute("SELECT * FROM hws WHERE id = ?", (hw_id,))
    return cur.fetchone()

def get_hws_by_object(object_name: str, only_active: bool = True):
    """
    Получить задания по предмету
    """
    if only_active:
        cur.execute("SELECT * FROM hws WHERE object = ? AND status = 'active'", 
                (object_name,))
    else:
        cur.execute("SELECT * FROM hws WHERE object = ?", (object_name,))
    return cur.fetchall()

class Week:
    def __init__(self, storage_file='.week.json'):
        self.storage_file = storage_file
        self.current_week = self._load_state()
    
    def _load_state(self):
        """Загружаем состояние из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    return data.get('week', 'числитель')
            except:
                return 'числитель'
        return 'числитель'
    
    def _save_state(self):
        """Сохраняет состояние в файл"""
        with open(self.storage_file, 'w') as f:
            json.dump({'week': self.current_week}, f)
    
    def next_week(self):
        """Переключает на следующую неделю и сохраняет"""
        self.current_week = 'знаменатель' if self.current_week == 'числитель' else 'числитель'
        self._save_state()
        return self.current_week
    
    def get_current_week(self) -> str:
        return self.current_week