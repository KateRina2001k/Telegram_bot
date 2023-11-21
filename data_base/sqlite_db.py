import sqlite3
from create_bot import bot 
import datetime
from sqlite3 import IntegrityError 

base = sqlite3.connect('independent_school.db')
cursor = base.cursor()

async def get_data_from_proxy(state):
    async with state.proxy() as data:
        return data

def sql_start():
    if base:
        print('База данных подключена')
    cursor.execute('CREATE TABLE IF NOT EXISTS users (tg_id, name_class,name_profile)')
    cursor.execute('CREATE TABLE IF NOT EXISTS users (dt DATETIME, title TEXT, content TEXT, img TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS grade (name TEXT PRIMARY KEY, schedule TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS distribution (name2 TEXT PRIMARY KEY, chart TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS questions (user_id INT, question TEXT, nick TEXT)')
    base.commit()

    async def add_news(state):
        proxy_data = await get_data_from_proxy(state)
        cursor.execute('INSERT INTO news VALUES (?, ?, ?, ?)', (datetime.now(),) + tuple(proxy_data.values()))
        base.commit()

    async def get_news():
        return[n for n in cursor.execute('SELECT * FROM news')]
    
async def delete_news(date):
    datetime_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    cursor.execute('DELETE FROM news WHERE dt = ?', (datetime_obj,))
    base.commit()

async def get_all_grades():
    return [_ for _ in cursor.execute('SELECT * FROM grades')]


async def get_all_users():
    return [u for u in cursor.execute('SELECT * FROM users')]


async def change_user_grade(user_id, grade_name):
    cursor.execute('UPDATE users SET name_grade = ? WHERE tg_id = ?', (grade_name, user_id))
    base.commit()

async def get_distributions():
    return [m for m in cursor.execute('SELECT * FROM distributions')]


async def get_all_users():
    return [u for u in cursor.execute('SELECT * FROM users')]


async def change_user_distribution(user_id,name2_profile):
    cursor.execute('UPDATE users SET name_profile = ? WHERE tg_id = ?', (name2_profile, user_id))
    base.commit()

async def delete_question(user_id):
    cursor.execute('DELETE FROM questions WHERE user_id = ?', (user_id,))
    base.commit()


def get_all_questions():
    return [_ for _ in cursor.execute('SELECT * FROM questions')]


async def add_question(state):
    data = await get_data_from_proxy(state)
    cursor.execute('INSERT INTO questions VALUES (?, ?, ?)', (data['user_id'],
                                                              data['question'],
                                                              data['nick'],
                                                              )
                   )
    base.commit()


async def get_grade(name):
    return [i for i in cursor.execute('SELECT * FROM grades WHERE name = ?', (name,))]


async def get_only_such_users(name):
    return [i for i in cursor.execute('SELECT * FROM users WHERE name_grade = ?', (name,))]


async def create_schedule(state):
    data = await get_data_from_proxy(state)
    cursor.execute('UPDATE grades SET schedule = ? WHERE name = ?',
                   (data['image'], data['grade']))
    base.commit()


async def delete_schedule(name):
    cursor.execute('UPDATE grades SET schedule = ? WHERE name = ?', (None, name))
    base.commit()


async def add_user(user_id):
    cursor.execute('INSERT INTO users VALUES (?, ?)', (user_id, 'no_grade'))
    base.commit()


async def get_data_from_proxy(state):
    async with state.proxy() as data:
        return data
    
async def delete_question(user_id):
    cursor.execute('DELETE FROM questions WHERE user_id = ?', (user_id,))
    base.commit()


def get_all_questions():
    return [_ for _ in cursor.execute('SELECT * FROM questions')]


async def add_question(state):
    data = await get_data_from_proxy(state)
    cursor.execute('INSERT INTO questions VALUES (?, ?, ?)', (data['user_id'],
                                                              data['question'],
                                                              data['nick'],
                                                              )
                   )
    base.commit()