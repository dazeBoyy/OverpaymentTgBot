from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from app.database.requests import get_overworks, get_overworks_data
from aiogram.utils.keyboard import  InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать новый учет переработок📝')],
                                    [KeyboardButton(text='Добавить в существующий учет💸')],
                                    [KeyboardButton(text='Изменить название учета переработок')],
                                    [KeyboardButton(text='Удалить учет❌')],
                                    [KeyboardButton(text='Вывод переработок в Exel📅'),
                                    KeyboardButton(text='Отправка переработок на почту📪')]],
                           resize_keyboard= True,
                           input_field_placeholder='Выберите пункт меню....')


new_accounting = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Название переработки')]],
                           resize_keyboard= True,
                           input_field_placeholder='Выберите пункт меню....')


add_overwork = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Добавить переработку')]],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню....')

async def overwork():
    all_overworks = await get_overworks()
    keyboard = InlineKeyboardBuilder()

    for overwork in all_overworks:
        keyboard.add(InlineKeyboardButton(text=f"{overwork.name}", callback_data=f"overwork_{overwork.id}"))

    return keyboard.adjust(1).as_markup()


async def overwork_data(overwork_id):
    all_overworks_data = await get_overworks_data(overwork_id)
    keyboard = InlineKeyboardBuilder()

    for data in all_overworks_data:
        keyboard.add(InlineKeyboardButton(text=f'{data.date} - {data.work} - {data.sum} - {data.budget}', callback_data=f"data_{data.id}"))
    return keyboard.adjust(1).as_markup()

