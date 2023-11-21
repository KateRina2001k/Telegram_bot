from aiogram import types


def grade_keyboard(grade_list):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for grade in grade_list:
        but = types.KeyboardButton(grade[0])
        kb.add(but)
    return kb

def distribution_keyboard(distribution_list):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for distribution in distribution_list:
        but = types.KeyboardButton(distribution[0])
        kb.add(but)
    return kb