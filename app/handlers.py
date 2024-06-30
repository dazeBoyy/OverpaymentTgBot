import logging

from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F, types
import app.keyboards as keyboard
import app.database.requests as rq


router = Router()


class NewAccounting(StatesGroup):
    accounting_name = State()


class NewOverWork(StatesGroup):
    accounting_id = State()
    date = State()
    work_name = State()
    sum = State()
    budget = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(text='Добро пожаловать в бота по учету переработок 👻',
                         reply_markup=keyboard.main)


@router.message(F.text == 'Создать новый учет переработок 📊')
async def new_accounting(message: Message,  state: FSMContext) -> None:
    await state.set_state(NewAccounting.accounting_name)
    await message.answer(
        "Введите название для учета", reply_markup=types.ReplyKeyboardRemove()
    )
    # await rq.add_overwork(message.from_user, message.from_user.id)


@router.message(NewAccounting.accounting_name)
async def set_accounting_name(message: Message,  state: FSMContext) -> None:
    await state.update_data(accounting_name=message.text)
    data = await state.get_data()
    await rq.add_accounting(data['accounting_name'],
                            message.from_user.id
                            )
    await message.answer(
        f"Новый учёт успешно создан! Теперь вы можете записывать ваши переработки, перейдя в раздел 'Весь список переработок'. Выберите только что созданный учёт или добавьте данные в уже существующий. 📝✨", reply_markup=keyboard.main)
    await state.clear()


@router.message(F.text == 'Все учёты 💼')
async def get_overwork(message: Message):
    await message.answer('Выбирите переработку в которую хотите добавить данные',
                         reply_markup=await keyboard.overwork(message.from_user.id))


@router.callback_query(F.data.startswith('overwork_'))
async def get_overwoks_data(callBack: CallbackQuery, state: FSMContext):
    accounting_id = callBack.data.split('_')[1]
    await callBack.message.answer('Весь список переработок: ',
                                  reply_markup= await keyboard.overwork_data(callBack.data.split('_')[1]))
    await callBack.message.answer('Выберите действие:', reply_markup=await keyboard.overwork_data_regular())
    await state.update_data(accounting_id=accounting_id)

@router.message(F.text == 'Добавить переработку')
async def add_overwork(message: Message,  state: FSMContext):
    await state.set_state(NewOverWork.date)
    await message.answer(
        "Введите дату переработки в формате дд.мм", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(NewOverWork.date)
async def set_date(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text)
    await state.set_state(NewOverWork.work_name)
    await message.answer(
        "Опишите работу которую вы выполняли", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(NewOverWork.work_name)
async def set_work_name(message: Message, state: FSMContext) -> None:
    await state.update_data(work_name=message.text)
    await state.set_state(NewOverWork.sum)
    await message.answer(
        "Введите сумму работы", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(NewOverWork.sum)
async def set_date(message: Message, state: FSMContext) -> None:
    await state.update_data(sum=message.text)
    await state.set_state(NewOverWork.budget)
    await message.answer(
        "Введите чей был бюджет", reply_markup=types.ReplyKeyboardRemove()
    )


@router.message(NewOverWork.budget)
async def set_budget(message: Message, state: FSMContext) -> None:
    await state.update_data(budget=message.text)
    data = await state.get_data()
    await rq.add_overwork(  data['date'],
                            data['work_name'],
                            data['sum'],
                            data['budget'],
                            data['accounting_id']
                            )
    await message.answer(
        f"Данные записаны:)", reply_markup=keyboard.main)
    await state.clear()


@router.message(F.text == 'На главную')
async def back_to_main(message: Message):
    await message.answer("Вы вернулись на главную страничку", reply_markup=keyboard.main)