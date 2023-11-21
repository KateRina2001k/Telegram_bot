from aiogram import types
from create_bot import bot, dp, ADMINS_CHAT_ID 
from handlers.states import NewsStates
from handlers import states
from aiogram.dispatcher import FSMContext
from data_base import sqlite_db
from keyboards import inline_kb, delete_kb, commonly_kb
from aiogram.dispatcher.filters import Text
from handlers import sending_mess
from create_bot import ADMINS_CHAT_ID
from data_base.sqlite_db import get_data_from_proxy


async def add_proxy_data(state, data):
    async with state.proxy() as proxy:
        for k,v in data.items():
            proxy[k] = v

@dp.message_handler(commands=['create_news'])
async def create_news(message: types.Message):
    await NewsStates.title.set()
    await message.reply('Отправьте заголовок новости', reply=False)


@dp.message_handler(state=NewsStates.title)
async def state_title_news(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'title': message.text})
    await message.reply('Введите содержание новости', reply=False)
    await NewsStates.next()

@dp.message_handler(state=NewsStates.content)
async def state_content_news(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'content': message.text})
    await message.reply('Введите содержание новости', reply=False)
    await NewsStates.next()

@dp.message_handler(state=NewsStates.image, content_types=['photo'])
async def state_image_news(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'image': message.photo[0].file_id})
    await sqlite_db.add_news(state)
    await message.reply('Новость успешно создана', reply=False)
    await state.finish()
    
@dp.message_handler(commands=['delete news'])
async def delete_news(message: types.Message):
    news = await sqlite_db.get_news()
    for i in news:
        await bot.send_photo(message.chat,id, i[3], f'*НОВОСТЬ*\n\n {i[1]}\n{i[2]}',
                             parse_mode='Markdown', reply_markup=inline_kb.create_delete_news_keyboard(i[0]))


@dp.callback_query_handler(Text(startswith='news '))
async def callback_delete_news(callback: types.CallbackQuery):
    cb_data = callback.data.replace('news ', '')
    await sqlite_db.delete_news(cb_data)
    await delete_kb.delete_inline_keyboards(callback.message)
    await callback.answer('Новость удалена')
    await bot.send_message(callback.message.chat.id, 'Новость успешно удалена!')

@dp.message_handler(commands=['create_grade'], is_chat_admin=True)
async def create_grade_command(message: types.Message):
    await message.reply('Введите название класса')
    await states.CreateGradeStates.grade_name.set()

@dp.message_handler(commands=['create_distribution'], is_chat_admin=True)
async def create_distributione_command(message: types.Message):
    await message.reply('Введите название профиля')
    await states.CreateGradeStates.distribution_name.set()

@dp.message_handler(commands=['create_schedule'], is_chat_admin=True)
async def create_schedule(message: types.Message):
    grades = await sqlite_db.get_all_grades()
    await states.ScheduleStates.select_grade.set()
    await message.reply('Выберите класс, в котором хотите обновить расписание', reply=False,
                        reply_markup=commonly_kb.grade_keyboard(grades))


@dp.message_handler(state=states.ScheduleStates.select_grade)
async def state_select_grade_schedule(message: types.Message, state: FSMContext):
    all_grades_names = [name[0] for name in await sqlite_db.get_all_grades()]
    if message.text in all_grades_names:
         await add_proxy_data(state, {'grade': message.text})
         if message.text == "10" or message.text == "11":
          await sqlite_db.change_user_distribution(message.from_user.id, message.text)
         await message.reply('Выберите профиль обучения', reply=False,
                                reply_markup=commonly_kb.distributione_keyboard())
         await states.ScheduleStates.next()
    else:
         await message.reply('Теперь отправьте фотографию расписания', reply=False,
                            reply_markup=types.ReplyKeyboardRemove())
    await states.ScheduleStates.next()
    await state.finish()


@dp.message_handler(state=states.ScheduleStates.image, content_types=['photo'])
async def state_image_schedule(message: types.Message, state: FSMContext):
    await add_proxy_data(state, {'image': message.photo[0].file_id})
    await sqlite_db.create_schedule(state)
    await message.reply('Расписание добавлено', reply=False)
    async with state.proxy() as data:
        await sending_mess.sending_schedule(data['grade'])
    await state.finish()


@dp.message_handler(commands=['delete_schedule'], is_chat_admin=True)
async def delete_schedule(message: types.Message):
    grades = await sqlite_db.get_all_grades()
    kb = commonly_kb.grade_keyboard(grades)
    await message.reply('Выберите расписание класса, которое хотите удалить', reply=False,
                        reply_markup=kb)
    await states.DeleteScheduleStates.select_grade.set()


@dp.message_handler(state=states.DeleteScheduleStates.select_grade)
async def state_delete_schedule(message: types.Message, state: FSMContext):
    all_grades_names = [name[0] for name in await sqlite_db.get_all_grades()]
    if message.text in all_grades_names:
        if message.text == "10" or message.text == "11":
         await sqlite_db.change_user_distribution(message.from_user.id, message.text)
         await message.reply('Выберите профиль, для которого хотите удалить расписание', reply=False,
                                reply_markup=commonly_kb.distribution_keyboard())
         await states.DeleteScheduleStates.next()
        else:
         await sqlite_db.delete_schedule(message.text)
        await message.reply(f'Расписание класса - {message.text} удалено', reply=False,
                            reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    else:
        await bot.send_message(message.chat.id, 'Такого класса не существует!')
        await state.finish()


@dp.message_handler(commands=['next_reply'], is_chat_admin=True)
async def next_reply_command(message: types.Message):
    all_qtns = sqlite_db.get_all_questions()
    if all_qtns:
        await states.AnswerTheQuestion.start.set()
        await bot.send_message(ADMINS_CHAT_ID, f'Вопрос от @{all_qtns[0][2]}:\n'
                                               f'{all_qtns[0][1]}',
                               reply_markup=await inline_kb.create_reply_keyboard(all_qtns[0][0]))
    else:
        await bot.send_message(ADMINS_CHAT_ID, 'Вопросы закончились')


@dp.callback_query_handler(Text(startswith='qtn '), state=states.AnswerTheQuestion.start)
async def callback_question_and_start_state(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.replace('qtn ', '')
    await add_proxy_data(state, {'user_id': user_id})
    await states.AnswerTheQuestion.next()
    await callback.message.reply('Введите ответ пользователю', reply=False)
    await callback.answer()


@dp.message_handler(state=states.AnswerTheQuestion.answer)
async def answer_the_question(message: types.Message, state: FSMContext):
    dict_from_proxy = await get_data_from_proxy(state)
    await bot.send_message(int(dict_from_proxy['user_id']), 'На Ваш вопрос ответили: \n'
                                                            f'{message.text}')
    await message.reply('Пользователь получил Ваш ответ!', reply=False)
    await sqlite_db.delete_question(int(dict_from_proxy['user_id']))
    await state.finish()