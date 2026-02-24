import asyncio
import logging
from datetime import datetime, timezone, timedelta

from aiogram import Bot, Dispatcher

from config import config
from handlers import routers, days_until_deadline
from constants import FORUM_ID, TOPIC_ID, DAILY_HW_TEXT
from database import get_active_hws, mark_as_outdated, Week
from middlwares import PrivateChatMiddleware


logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # Команды пришиваем
    for router in routers:
        dp.include_router(router)
    
    poster = DailyPoster(bot)
    poster_task = asyncio.create_task(poster.start_daily_posting())

    dp.message.middleware.register(PrivateChatMiddleware())

    logging.info("Негр пашет")
    await dp.start_polling(bot)

def genocide_outdated_hws():
    hws = get_active_hws()
    for hw in hws:
        if days_until_deadline(hw[5]) == 0:
            mark_as_outdated(hw[0])

class DailyPoster:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.is_running = False
        
    async def start_daily_posting(self):
        """Запускает ежедневную отправку сообщений"""
        self.is_running = True
        last_post_day = None  # Чтобы не отправлять несколько раз в один день
        logging.info("Daily poster is active")
        msc_tz = timezone(timedelta(hours=3))
        
        while self.is_running:
            try:
                now = datetime.now(msc_tz)
                
                if (now.hour == 18 and last_post_day != now.date) and now.weekday() != 5:
                    genocide_outdated_hws()
                    # Проверяем, что сегодня еще не отправляли
                    if last_post_day != now.date():
                        await self.send_daily_message()
                        last_post_day = now.date()
                        logging.info("Ежедневное сообщение было отправлено")
                
                elif now.weekday() == 5:
                    wek = Week()
                    wek.next_week()
                
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                await asyncio.sleep(10)
    
    async def send_daily_message(self):
        """Отправляет ежедневное сообщение"""
        try:
            wek = Week()
            week = wek.get_week()
            text = f"Текущая неделя: {week.capitalize()} ДЗ на завтра:"
            if get_active_hws() == []:
                await self.bot.send_message(
                    chat_id=FORUM_ID,
                    message_thread_id=TOPIC_ID, 
                    text=f"*На завтра ДЗ в базе данных отсутствует*\n Текущая неделя: {week.capitalize()}",
                    parse_mode="MarkdownV2",
                    disable_notification=True
                )
                return 1
                
            for hw in get_active_hws():
                if days_until_deadline(hw[5]) == 1 or hw[5] == "undefined":
                    text = text + DAILY_HW_TEXT.format(hw[1].capitalize(), hw[0], len(eval(hw[3])), hw[2], hw[4], hw[5])
            text += "Для подробностей обращаться к боту в лс"
            await self.bot.send_message(
                chat_id=FORUM_ID,
                message_thread_id=TOPIC_ID, 
                text=text,
                parse_mode="MarkdownV2",
                disable_notification=True
            )
            
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение: {e}")
    
    async def stop(self):
        """Останавливает отправку"""
        self.is_running = False


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Убили негра")
