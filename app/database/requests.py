from app.database.models import async_session, OverWorkData
from app.database.models import User, OverWork
from sqlalchemy import select, update, delete, insert

async def set_user(tg_id) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()

async def get_overworks():
    async with async_session() as session:
        return await session.scalars(select(OverWork))


async def get_overworks_data(overwork_id):
    async with async_session() as session:
        return await session.scalars(select(OverWorkData).where(OverWorkData.overwork_id == overwork_id))