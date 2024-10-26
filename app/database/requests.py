import datetime

<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession

=======
>>>>>>> 5805494cbb35c06feb099c107799c6658803b50e
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


<<<<<<< HEAD
async def change_overwork(overwork_id, data) -> None:
    async with async_session() as session:
        result = await session.execute(
            select(OverWorkData)
            .where(OverWorkData.id == overwork_id)
        )
        overwork_to_change = result.scalars().first()
        date = data.get('date')

        # Проверяем, является ли `date` строкой или объектом datetime
        if isinstance(date, str):
            # Если строка, форматируем её и добавляем текущий год
            date = datetime.strptime(date, '%d.%m').replace(year=datetime.now().year)
        elif isinstance(date, datetime):
            # Если уже datetime, просто добавляем текущий год, если это необходимо
            date = date.replace(year=datetime.now().year)
        if overwork_to_change:
            # Извлекаем данные из словаря и обновляем поля
            overwork_to_change.date = date
            overwork_to_change.work = data.get('work_name')
            overwork_to_change.sum = data.get('sum')
            overwork_to_change.budget = data.get('budget')
            overwork_to_change.picture = data.get('picture')

            await session.commit()
        else:
            print(f"Переработка с ID {overwork_id} не найдена.")


async def delete_overwork(overwork_id):
    async with async_session() as session:
        overwork_to_delete = await session.get(OverWorkData, overwork_id)

        if overwork_to_delete:
            await session.delete(overwork_to_delete)
            await session.commit()


=======
>>>>>>> 5805494cbb35c06feb099c107799c6658803b50e
async def get_accounting_info_orm(accounting_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Accounting)
            .where(Accounting.id == accounting_id)
        )
        return result.scalars().first()

<<<<<<< HEAD

=======
>>>>>>> 5805494cbb35c06feb099c107799c6658803b50e
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
<<<<<<< HEAD


async def get_accounting_data(accounting_id):
    async with async_session() as session:
        # Получаем данные переработок, связанные с учётом
        result = await session.scalars(
            select(OverWorkData)
                .where(OverWorkData.accounting_id == accounting_id)
                .order_by(asc(OverWorkData.date))
        )
        overworks_data = result.all()

        # Получаем название учёта для использования в названии файла
        accounting = await session.get(Accounting, accounting_id)
        accounting_name = accounting.name if accounting else "учет"

        return {
            "data": [
                {
                    "date": row.date.strftime("%d.%m.%Y"),
                    "work": row.work,
                    "sum": row.sum,
                    "budget": row.budget,
                }
                for row in overworks_data
            ],
            "name": accounting_name  # Возвращаем название учёта
        }
=======
>>>>>>> 5805494cbb35c06feb099c107799c6658803b50e
