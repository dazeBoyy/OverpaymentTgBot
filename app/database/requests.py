import datetime

from app.database.models import async_session, OverWorkData
from app.database.models import User, Accounting
from sqlalchemy import select, update, delete, insert, asc
from datetime import datetime


async def set_user(tg_id) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()


async def add_accounting(accounting_name,
                         user_id
                         ) -> None:
    async with async_session() as session:
        session.add(Accounting(name=accounting_name,
                             user_id=select(User.id)
                             .where(User.tg_id == user_id).scalar_subquery()))
        await session.commit()


async def add_overwork(date, overwork_name, sum, budget, picture, accounting_id
                         ) -> None:
    # Преобразование строки даты в объект datetime
    date = datetime.strptime(date, '%d.%m')
    # Обновление года для сохранения корректной даты (например, текущий год)
    date = date.replace(year=datetime.now().year)

    async with async_session() as session:
        session.add(OverWorkData(date=date,
                                 work=overwork_name,
                                 sum=sum,
                                 budget=budget,
                                 picture=picture,
                                 accounting_id=select(Accounting.id)
                                 .where(Accounting.id == accounting_id).scalar_subquery()))
        await session.commit()


async def get_accountings(user_id):
    async with async_session() as session:
        return await session.scalars(select(Accounting)
                                     .where(Accounting.user_id == select(User.id)
                                            .where(User.tg_id == user_id).scalar_subquery()))


async def get_overworks_data(accounting_id):
    async with async_session() as session:
        return await session.scalars(select(OverWorkData).where(OverWorkData.accounting_id == accounting_id).order_by(asc((OverWorkData.date))))

async def get_overwork(overwork_id):
    async with async_session() as session:
        result = await session.execute(
            select(OverWorkData)
            .where(OverWorkData.id == overwork_id)
        )
        return result.scalars().first()


async def get_accounting_info_orm(accounting_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Accounting)
            .where(Accounting.id == accounting_id)
        )
        return result.scalars().first()

async def delete_accounting_orm(accounting_id: int):
    async with async_session() as session:
        accounting_to_delete = await session.get(Accounting, accounting_id)
        if accounting_to_delete:
            await session.delete(accounting_to_delete)
            await session.commit()



async def change_accounting(accounting_id,
                            accounting_name) -> None:
    async with async_session() as session:
        # Получаем объект учёта из базы данных
        accounting_to_change = await session.get(Accounting, accounting_id)

        if accounting_to_change:
            # Вносим изменения в объект учёта
            accounting_to_change.name = accounting_name

            # Сохраняем изменения в базе данных
            await session.commit()
        else:
            # Обработка случая, если учёт с заданным ID не найден
            print(f"Учёт с ID {accounting_id} не найден.")
