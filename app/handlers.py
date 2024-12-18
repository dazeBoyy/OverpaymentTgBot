import asyncio
import re

import aiofiles
from aiofiles import os
from aiogram.client import bot
from aiogram.filters import CommandStart, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from aiogram import Router, F, types
from excel_utils import generate_excel
import app.keyboards as keyboard
import app.database.requests as rq



router = Router()


class NewAccounting(StatesGroup):
    accounting_name = State()

    accounting_for_change = None


class NewOverWork(StatesGroup):
    accounting_id = State()
    date = State()
    work_name = State()
    sum = State()
    budget = State()
    picture = State()

    overwork_for_change = None




@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(text='Добро пожаловать в бота по учету переработок 👻',
                         reply_markup=keyboard.main)

# Хендлер отмены и сброса состояния должен быть всегда именно хдесь,
# после того как только встали в состояние номер 1 (элементарная очередность фильтров)


@router.message(F.text == 'Все учёты 💼')
async def get_accountings(message: Message):
    await message.answer('Выберите переработку в которую хотите добавить данные:',
                         reply_markup=await keyboard.accountings(message.from_user.id))
    await message.answer('Либо, выберите действие с учётом переработок, используя кнопки ниже:', reply_markup=keyboard.accounting_buttons)


@router.message(F.text == 'Удалить учёт 🗑️')
async def delete_accounting(message: Message):
    await message.answer('Выберите учет который вы хотите удалить:',
                         reply_markup=await keyboard.delete_accountings(message.from_user.id))

@router.message(F.text == 'Изменить название учета переработок ✏️')
async def change_accounting(message: Message):
    await message.answer('Выберите учет, название которого вы хотите изменить🔁:',
                         reply_markup=await keyboard.change_accountings(message.from_user.id))


@router.callback_query(F.data.startswith('change_'))
async def change_accounting_callback(callBack: CallbackQuery, state: FSMContext,):
    accounting_id = callBack.data.split('_')[1]
    accounting_for_change = await rq.get_accounting_info_orm(accounting_id)

    NewAccounting.accounting_for_change = accounting_for_change

    await callBack.answer()
    await callBack.message.answer(
        "Введите название учёта:", reply_markup=keyboard.skip_button
    )
    await state.set_state(NewAccounting.accounting_name)


@router.message(F.text == 'Создать новый учет переработок 📊')
async def new_accounting(message: Message,  state: FSMContext) -> None:
    await state.set_state(NewAccounting.accounting_name)
    await message.answer(
        "Введите название для учета:", reply_markup=keyboard.cancel
    )
@router.message(StateFilter(NewAccounting.accounting_name), F.text == "Отмена")
@router.message(StateFilter("*"), F.text == "Отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действие отменены⛔", reply_markup=keyboard.main)

@router.message(NewAccounting.accounting_name, or_f(F.text, F.text == "Пропустить"))
async def set_accounting_name(message: Message,  state: FSMContext) -> None:
    if message.text == "Пропустить":
        await state.update_data(accounting_name=NewAccounting.accounting_for_change.name)
    else:
        if message.content_type != 'text':
            await message.answer(
                "Пожалуйста, введите текстовое описание работы, не более 90 символов."
            )
            return
        if not message.text.strip():
            await message.answer("Вы не ввели название учета 💀. Введите заново.")
            return 
        elif len(message.text) >= 90:
            await message.answer(
                "Название слегка большое 🤏 \n Введите заново"
            )
            return
        await state.update_data(accounting_name=message.text)
    data = await state.get_data()
    if NewAccounting.accounting_for_change:
        await rq.change_accounting(NewAccounting.accounting_for_change.id,
                                   data['accounting_name']
        )
    else:
        await rq.add_accounting(data['accounting_name'],
                                message.from_user.id
                                )
    await message.answer(
        f"Учёт успешно создан, либо был изменен! Теперь вы можете записывать ваши переработки, перейдя в раздел 'Все учёты'. И выбрать, только что созданный учёт или добавить данные, в уже существующий. 📝✨", reply_markup=keyboard.main)
    await state.clear()
    NewAccounting.accounting_for_change = None


@router.callback_query(F.data.startswith('delete_'))
async def delete_accounting_callback(callBack: CallbackQuery):
    accounting_id = callBack.data.split('_')[1]
    await rq.delete_accounting_orm(int(accounting_id))
    await callBack.answer("Учёт удалён❌")
    await callBack.message.answer("Учёт удалён!❌")


@router.callback_query(F.data.startswith('overwork_'))
async def get_overwoks_data(callBack: CallbackQuery, state: FSMContext):
    accounting_id = callBack.data.split('_')[1]
    await callBack.message.answer('Весь список переработок📃: ',
                                  reply_markup= await keyboard.overwork_data(callBack.data.split('_')[1]))
    await callBack.message.answer('Выберите действие:', reply_markup=await keyboard.overwork_data_regular())
    await state.update_data(accounting_id=accounting_id)


@router.callback_query(F.data.startswith('data_'))
async def get_overwork(callBack: CallbackQuery):
    overwork_id = callBack.data.split('_')[1]
    overwork_data = await rq.get_overwork(overwork_id)
    formatted_date = overwork_data.date.strftime("%d.%m")
    caption = f"<b>Дата:</b> {formatted_date}\n" \
              f"<b>Работа:</b> {overwork_data.work}\n" \
              f"<b>Сумма:</b> {round(overwork_data.sum, 2)} руб\n" \
              f"<b>Бюджет:</b> {overwork_data.budget}"
    await callBack.message.answer('Выберите действие:', reply_markup=keyboard.on_main)
    await callBack.message.answer_photo(
        photo=overwork_data.picture,
        caption=caption,
        reply_markup=await keyboard.overwork_data_action(overwork_data.id),
        parse_mode='HTML'  # Указываем HTML для поддержки форматирования
    )


@router.callback_query(F.data.startswith('overworkchange_'))
async def change_overwork_callback(callBack: CallbackQuery, state: FSMContext,):
    overwork_id = callBack.data.split('_')[1]
    overwork_for_change = await rq.get_overwork(overwork_id)

    NewOverWork.overwork_for_change = overwork_for_change
    await state.update_data(is_editing=True)

    await callBack.answer()
    await callBack.message.answer(
        "Введите дату переработки в формате дд.мм:", reply_markup=keyboard.skip_and_cancel
    )
    await state.set_state(NewOverWork.date)


@router.callback_query(F.data.startswith('overworkdelete_'))
async def delete_overwork_callback(callBack: CallbackQuery):
    overwork_id = callBack.data.split('_')[1]
    await rq.delete_overwork(int(overwork_id))
    await callBack.answer("Переработка удалёна!❌")
    await callBack.message.answer("Переработка удалёна!❌")


@router.message(F.text == 'Добавить переработку')
async def add_overwork(message: Message,  state: FSMContext):
    await state.set_state(NewOverWork.date)
    await message.answer(
        "Введите дату переработки в формате дд.мм:", reply_markup=keyboard.cancel
    )


@router.message(NewOverWork.date,  or_f(F.text, F.text == "Пропустить"))
async def set_date(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    is_editing = data.get('is_editing', False)
    if message.text == "Пропустить" and is_editing:
        await state.update_data(date=NewOverWork.overwork_for_change.date)
    else:
        date_pattern = re.compile(r'^\d{2}\.\d{2}$')
        if not date_pattern.match(message.text):
            await message.answer(
                "Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ, например, 05.01:"
            )
            return

        await state.update_data(date=message.text)
    await state.set_state(NewOverWork.work_name)
    reply_markup = keyboard.skip_and_cancel if is_editing else keyboard.cancel
    await message.answer(
        "Опишите работу, которую вы выполняли:", reply_markup=reply_markup
    )


@router.message(NewOverWork.work_name, or_f(F.text, F.text == "Пропустить"))
async def set_work_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    is_editing = data.get('is_editing', False)
    if message.text == "Пропустить" and is_editing:
        await state.update_data(work_name=NewOverWork.overwork_for_change.work)
    else:
        if message.content_type != 'text':
            await message.answer(
                "Пожалуйста, введите текстовое описание работы, не более 120 символов."
            )
            return

        work_name = message.text.strip()

        if not work_name:
            await message.answer(
                "Вы не ввели описание работы. Пожалуйста, введите заново:"
            )
            return

        if len(work_name) > 120:
            await message.answer(
                "Описание работы не должно превышать 120 символов. Пожалуйста, введите заново:"
            )
            return
        await state.update_data(work_name=message.text)
    await state.set_state(NewOverWork.sum)
    reply_markup = keyboard.skip_and_cancel if is_editing else keyboard.cancel
    await message.answer(
        "Введите сумму работы:", reply_markup=reply_markup
    )


@router.message(NewOverWork.sum, or_f(F.text, F.text == "Пропустить"))
async def set_date(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    is_editing = data.get('is_editing', False)
    if message.text == "Пропустить" and is_editing:
        await state.update_data(sum=NewOverWork.overwork_for_change.sum)
    else:
        sum_value = message.text.strip()
        if not sum_value.isdigit():
            await message.answer(
                "Сумма должна содержать только цифры. Пожалуйста, введите заново:"
            )
            return
        await state.update_data(sum=int(message.text))
    await state.set_state(NewOverWork.budget)
    reply_markup = keyboard.skip_and_cancel if is_editing else keyboard.cancel
    await message.answer(
        "Введите чей был бюджет:", reply_markup=reply_markup
    )


@router.message(NewOverWork.budget, or_f(F.text, F.text == "Пропустить"))
async def set_budget(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    is_editing = data.get('is_editing', False)
    if message.text == "Пропустить" and is_editing:
        await state.update_data(budget=NewOverWork.overwork_for_change.budget)
    else:
        if message.content_type != 'text':
            await message.answer(
                "Пожалуйста, введите текстовое описание работы, не более 50 символов."
            )
            return

        budget = message.text.strip()

        if not budget:
            await message.answer(
                "Вы не ввели описание работы. Пожалуйста, введите заново:"
            )
            return

        if len(budget) > 50:
            await message.answer(
                "Описание работы не должно превышать 50 символов. Пожалуйста, введите заново:"
            )
            return
        await state.update_data(budget=message.text)
    await state.set_state(NewOverWork.picture)
    await message.answer(
        "Отправьте фото того, что вы делали, или нажмите кнопку 'Пропустить', если оно не требуется:", reply_markup=keyboard.skip_and_cancel
    )

@router.message(NewOverWork.picture, or_f(F.photo, F.text == "Пропустить"))
async def set_picture(message: Message, state: FSMContext) -> None:
    if message.text and message.text == "Пропустить":
        await state.update_data(picture='AgACAgIAAxkBAAIDcGaJorBVLdDkgRvGt_HYMaKCjWnqAAJR5jEbNqNQSOOJ6-10w1x5AQADAgADeQADNQQ')
    else:
        await state.update_data(picture=message.photo[-1].file_id)
    data = await state.get_data()
    overwork_id = NewOverWork.overwork_for_change.id if NewOverWork.overwork_for_change else None

    if overwork_id:
        await rq.change_overwork(NewOverWork.overwork_for_change.id, data)
    else:
        await rq.add_overwork(  data['date'],
                                data['work_name'],
                                data['sum'],
                                data['budget'],
                                data['picture'],
                                data['accounting_id']
                                )
    await message.answer(
        f"Данные записаны✔️", reply_markup=keyboard.main)
    await state.clear()
    NewOverWork.overwork_for_change = None


@router.message(F.text == "Вывод переработок в Exсel 📈")
async def send_accounting_options(message: Message):

    await message.answer("Выберите учёт для экспорта в Excel:", reply_markup=await keyboard.export_to_excel(message.from_user.id))



@router.callback_query(F.data.startswith("export_excel_"))
async def export_to_excel(callBack: CallbackQuery):
    accounting_id = callBack.data.split("_")[2]

    accounting_data = await rq.get_accounting_data(accounting_id)
    data = accounting_data["data"]
    accounting_name = accounting_data["name"]

    # Убедитесь, что data содержит словари с нужными ключами
    if not all(key in entry for entry in data for key in ['date', 'work', 'sum', 'budget']):
        await callBack.message.answer("Некорректные данные для экспорта.")
        return

    try:
        excel_file = await generate_excel(data, accounting_name)
        await asyncio.sleep(2)
        await callBack.message.answer_document(FSInputFile(excel_file))
        await os.remove(excel_file)
    except Exception as e:
        # Обработка исключений
        await callBack.message.answer("Произошла ошибка при обработке файла: " + str(e))

@router.message(F.text == 'На главную')
async def back_to_main(message: Message):
    await message.answer("Вы вернулись на главную страничку😊", reply_markup=keyboard.main)