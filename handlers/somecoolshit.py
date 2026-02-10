from datetime import datetime, date

def days_until_deadline(end_date_str: str) -> int:
    """
    Вычисляет сколько дней осталось до дедлайна
    
    Args:
        end_date_str: дата в формате DD.MM.YY (например, "25.12.24")
    
    Returns:
        int: количество дней до дедлайна
        (отрицательное число, если дедлайн уже прошел)
    """
    try:
        # Преобразуем строку в объект datetime
        end_date = datetime.strptime(end_date_str, "%d.%m.%y").date()
        
        # Получаем сегодняшнюю дату
        today = date.today()
        
        # Вычисляем разницу в днях
        delta = end_date - today
        return delta.days
    
    except ValueError:
        return 0

