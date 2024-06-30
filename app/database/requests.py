import datetime

from app.database.models import async_session, OverWorkData
from app.database.models import User, OverWork
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
        session.add(OverWork(name=accounting_name,
                             user_id=select(User.id)
                             .where(User.tg_id == user_id).scalar_subquery()))
        await session.commit()


async def add_overwork(date,overwork_name,sum,budget,accounting_id
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
                                 overwork_id=select(OverWork.id)
                                 .where(OverWork.id == accounting_id).scalar_subquery()))
        await session.commit()


async def get_overworks(user_id):
    async with async_session() as session:
        return await session.scalars(select(OverWork)
                                     .where(OverWork.user_id == select(User.id)
                                            .where(User.tg_id == user_id).scalar_subquery()))


async def get_overworks_data(overwork_id):
    async with async_session() as session:
        return await session.scalars(select(OverWorkData).where(OverWorkData.overwork_id == overwork_id).order_by(asc((OverWorkData.date))))


async def delete_overwork_data(overwork_id: int):
    async with async_session() as session:
        overwork_to_delete = await session.get(OverWorkData, overwork_id)
        if overwork_to_delete:
            session.delete(overwork_to_delete)
            await session.commit()