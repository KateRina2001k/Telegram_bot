from create_bot import bot
from data_base import sqlite_db


async def sending_schedule(name):
    users = await sqlite_db.get_only_such_users(name)
    grade = await sqlite_db.get_grade(name)
    for user in users:
        await bot.send_photo(user[0], grade[0][1], caption='РАСПИСАНИЕ ВАШЕЙ ГРУППЫ ОБНОВЛЕНО')