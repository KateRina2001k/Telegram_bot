from create_bot import bot 
from aiogram.utils import executor
from data_base import sqlite_db
from create_bot import dp
from handlers import admin_side, user_side

async def on_startup(_):
    sqlite_db.sql_start()
    print ('Bot online!')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)