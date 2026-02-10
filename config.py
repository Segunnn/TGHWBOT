import os
from dotenv import load_dotenv

load_dotenv() 

class Settings:
    def __init__(self):
        self.bot_token = os.getenv("TOKEN")
        
        if not self.bot_token:
            self.bot_token = ""
            raise ValueError("TOKEN в .env не найден")

config = Settings()
