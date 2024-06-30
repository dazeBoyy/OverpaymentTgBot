from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from app.database.requests import get_overworks, get_overworks_data
from aiogram.utils.keyboard import  InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать новый учет переработок 📊')],
                                    [KeyboardButton(text='Все учёты 💼')],
                                    [KeyboardButton(text='Изменить название учета переработок ✏️')],
                                    [KeyboardButton(text='Удалить учёт 🗑️')],
                                    [KeyboardButton(text='Вывод переработок в Exel 📈'),
                                    KeyboardButton(text='Отправка переработок на почту 📧')]],
                           resize_keyboard= True,
                           input_field_placeholder='Выберите пункт меню....')


new_accounting = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Название переработки')]],
                           resize_keyboard= True,
                           input_field_placeholder='Выберите пункт меню....')


add_overwork = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Добавить переработку')]],
                        resize_keyboard=True,
                        input_field_placeholder='Выберите пункт меню....')

async def overwork(user_id):
    all_overworks = await get_overworks(user_id)
    keyboard = InlineKeyboardBuilder()

    for overwork in all_overworks:
        keyboard.add(InlineKeyboardButton(text=f"{overwork.name}", callback_data=f"overwork_{overwork.id}"))

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
        keyboard.add(InlineKeyboardButton(text=f'{formatted_date} - {data.work} - {data.sum} - {data.budget}', callback_data=f"data_{data.id}"))

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

