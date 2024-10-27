from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from app.database.requests import get_accountings, get_overworks_data, get_overwork
from aiogram.utils.keyboard import  InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать новый учет переработок 📊')],
                                    [KeyboardButton(text='Все учёты 💼')],
                                    [KeyboardButton(text='Вывод переработок в Exсel 📈'),]],
                           resize_keyboard= True,
                           input_field_placeholder='Выберите пункт меню....')


new_accounting = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Название переработки')]],
                           resize_keyboard= True,
                           input_field_placeholder='Выберите пункт меню....')


add_overwork = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Добавить переработку')]],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню....')

skip_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Пропустить')]],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню....')

accounting_buttons = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Изменить название учета переработок ✏️')],
                                                   [KeyboardButton(text='Удалить учёт 🗑️')],
                                                   [KeyboardButton(text='На главную')],
                                                   ],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню....')
async def accountings(user_id):
    all_accountings = await get_accountings(user_id)
    keyboard = InlineKeyboardBuilder()

    for accounting in all_accountings:
        keyboard.add(InlineKeyboardButton(text=f"{accounting.name}", callback_data=f"overwork_{accounting.id}"))

    return keyboard.adjust(1).as_markup()

async def export_to_excel(user_id):
    all_accountings = await get_accountings(user_id)
    keyboard = InlineKeyboardBuilder()

    for accounting in all_accountings:
        keyboard.add(InlineKeyboardButton(text=f"{accounting.name}", callback_data=f"export_excel_{accounting.id}"))

    return keyboard.adjust(1).as_markup()

async def delete_accountings(user_id):
    all_accountings = await get_accountings(user_id)
    keyboard = InlineKeyboardBuilder()

    for accounting in all_accountings:
        keyboard.add(InlineKeyboardButton(text=f"{accounting.name}", callback_data=f"delete_{accounting.id}"))

    return keyboard.adjust(1).as_markup()

async def change_accountings(user_id):
    all_accountings = await get_accountings(user_id)
    keyboard = InlineKeyboardBuilder()

    for accounting in all_accountings:
        keyboard.add(InlineKeyboardButton(text=f"{accounting.name}", callback_data=f"change_{accounting.id}"))

    return keyboard.adjust(1).as_markup()
async def overwork_data(overwork_id):
    all_overworks_data = await get_overworks_data(overwork_id)

    if all_overworks_data == '':
        keyboard = InlineKeyboardBuilder()
        keyboard.add(InlineKeyboardButton(text="Здесь пока что пусто😭"))
        return keyboard.as_markup()

    keyboard = InlineKeyboardBuilder()

    for data in all_overworks_data:
        formatted_date = data.date.strftime("%d.%m")
        keyboard.add(InlineKeyboardButton(text=f'{formatted_date} - {data.work} - {data.sum} руб - {data.budget}', callback_data=f"data_{data.id}"))

    return keyboard.adjust(1).as_markup()


async def overwork_data_regular():
    # Создание обычной клавиатуры с кнопками
    regular_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Добавить переработку')],
            [KeyboardButton(text='На главную')]
        ],
        resize_keyboard=True
    )

    return regular_keyboard

async def overwork_data_action(overwork_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text=f"Изменить", callback_data=f"overworkchange_{overwork_id}"))
    keyboard.add(InlineKeyboardButton(text=f"Удалить", callback_data=f"overworkdelete_{overwork_id}"))
    return keyboard.adjust(1).as_markup()

skip_and_cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')],
                                       [KeyboardButton(text='Пропустить')]],  resize_keyboard=True,)

cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')],
                                                   ],  resize_keyboard=True,)

on_main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='На главную')],
                                                   ],  resize_keyboard=True,)

