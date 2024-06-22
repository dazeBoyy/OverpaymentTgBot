from datetime import datetime

import sa
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, func, Column, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import  AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now())

class OverWork(Base):
    __tablename__ = 'overworks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(90))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

class OverWorkData(Base):
    __tablename__ = 'overworkdatas'

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True))
    work: Mapped[str] = mapped_column(String(120))
    sum: Mapped[int] = mapped_column()
    budget: Mapped[str] = mapped_column(String(50))
    overwork_id: Mapped[int] = mapped_column(ForeignKey('overworks.id'))
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

