from aiogram import types
from create_bot import bot, dp
from data_base import sqlite_db
from aiogram.dispatcher import FSMContext
from handlers import states
from keyboards import commonly_kb
from handlers.admin_side import add_proxy_data



@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    all_users_id = [id_[0] for id_ in await sqlite_db.get_all_users()]
    if message.from_user.id not in all_users_id:
        await sqlite_db.add_user(message.from_user.id)

    await bot.send_message(message.chat.id, 'Здравствуй! Это бот, в котором можно узнать актуальную информацию о частной школе "Ломоносовский лицей". Помощь по командам /help')
    await bot.send_message(message.chat.id, 'Выбери класс в котором учишься, либо напиши любой текст'
                                            'чтобы пропустить это',
                           reply_markup=commonly_kb.grade_keyboard(await sqlite_db.get_all_grades()))
    await states.StartStates.grade_name.set()


@dp.message_handler(commands=['news', 'новости'])
async def news_command(message: types.Message):
    news = await sqlite_db.get_news()
    for i in news[:3]:
        await bot.send_photo(message.chat.id, i[3], f'*{i[1]}*\n\n{i[2]}',
                             parse_mode='Markdown')
        
@dp.message_handler(state=states.SelectGrageStates.grade_name)
async def select_grade_state(message: types.Message, state: FSMContext):
    all_grade_names = [_[0] for _ in await sqlite_db.get_all_grades()]
    if message.text in all_grade_names:
        await sqlite_db.change_user_grade(message.from_user.id, message.text)
        await bot.send_message(message.chat.id, f'Класс изменен',
                               reply_markup=types.ReplyKeyboardRemove())
    else:
        await bot.send_message(message.chat.id, 'Класс который Вы выбрали, не существует',
                               reply_markup=types.ReplyKeyboardRemove())
    await state.finish()

@dp.message_handler(state=states.StartStates.grade_name)
async def start_state(message: types.Message, state: FSMContext):
    all_grade_names = [_[0] for _ in await sqlite_db.get_all_grades()]
    if message.text in all_grade_names:
        await sqlite_db.change_user_grade(message.from_user.id, message.text)
        await bot.send_message(message.chat.id, f'Вы прикреплены к классу - {message.text}',
                               reply_markup=types.ReplyKeyboardRemove())
    else:
        await bot.send_message(message.chat.id, 'Вы пропустили выбор класса, но всегда можно'
                                                ' выбрать его с помощью /select_grade',
                               reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=['select_grade'])
async def select_grade_command(message: types.Message):
    all_grades = await sqlite_db.get_all_grades()
    grade_kb = commonly_kb.grade_keyboard(all_grades)
    await message.reply('Выберите класс', reply=False,
                        reply_markup=grade_kb)
    await states.SelectGradeStates.grade_name.set()

    @dp.message_handler(commands=['delete_me_from_grade'])
    async def delete_from_grade(message: types.Message):
     await sqlite_db.change_user_grade(message.from_user.id, None)
     await message.reply('Класс успешно отвязан', reply=False)

@dp.message_handler(state=states.SelectGrage2States.distribution_name)
async def select_distribution_state(message: types.Message, state: FSMContext):
    all_distribution_names = [_[0] for _ in await sqlite_db.get_distributions()]
    if message.text == "10" or message.text == "11":
        await sqlite_db.change_user_distribution(message.from_user.id, message.text)  
        await bot.send_message(message.chat.id, f'Профиль обучения изменен',
                            reply_markup=types.ReplyKeyboardRemove())
    else:
        await bot.send_message(message.chat.id, 'Профиль обучения который Вы выбрали, не существует',
                               reply_markup=types.ReplyKeyboardRemove())
        await state.finish()

@dp.message_handler(state=states.StartStates.distribution_name)
async def start_state(message: types.Message, state: FSMContext):
    all_distribution_names = [_[0] for _ in await sqlite_db.get_distributions()]
    if message.text == "10" or message.text == "11":
         await sqlite_db.change_user_distribution_(message.from_user.id, message.text)
         await bot.send_message(message.chat.id, f'Вы прикреплены к профилю обучения - {message.text}',
                               reply_markup=types.ReplyKeyboardRemove())
    else:
        await bot.send_message(message.chat.id, 'Вы пропустили выбор профиля обучения, но всегда можно'
                                                ' выбрать его с помощью /select_distribution',
                               reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=['select_distribution'])
async def select_distribution_command(message: types.Message):
    all_distributions = await sqlite_db.get_distributions()
    distribution_kb = commonly_kb.distribution_keyboard(all_distributions)
    await message.reply('Выберите профиль обучения', reply=False,
                        reply_markup=distribution_kb)
    await states.SelectGrade2States.distribution_name.set()


@dp.message_handler(commands=['ask_question'])
async def ask_question_command(message: types.Message):
    await message.reply('Напишите свой вопрос', reply=False)
    await states.AskQuestionStates.get_question.set()


@dp.message_handler(state=states.AskQuestionStates.get_question)
async def get_question_state(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {
        'user_id': message.from_user.id,
        'question': message.text,
        'nick': message.from_user.username,
    })
    await sqlite_db.add_question(state)
    await message.reply('Вопрос задан, ждите ответа...', reply=False)


@dp.message_handler(commands=['id'])
async def get_grade_id(message: types.Message, state: FSMContext):
    await message.reply(message.chat.id)