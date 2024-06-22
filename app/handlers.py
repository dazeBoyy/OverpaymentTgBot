from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
import app.keyboards as keyboard
import app.database.requests as rq

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer(text='Добро пожаловать в бота по учету переработок 👻',
                         reply_markup=keyboard.main)


@router.message(F.text == 'Создать новый учет переработок📝')
async  def new_accounting(message: Message):
    await message.answer('Введите название для учета переработок',
                         reply_markup=keyboard.new_accounting)

@router.message(F.text == 'Добавить в существующий учет💸')
async def get_overwork(message: Message):
    await message.answer('Выбирите переработку в которую хотите добавить данные',
                         reply_markup=await keyboard.overwork())

@router.callback_query(F.data.startswith('overwork_'))
async def get_overwoks_data(callBack: CallbackQuery):
    await callBack.message.answer('Весь список переработок: ',
                                  reply_markup= await keyboard.overwork_data(callBack.data.split('_')[1]))