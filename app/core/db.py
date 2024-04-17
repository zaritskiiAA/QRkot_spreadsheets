from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, CheckConstraint
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from app.core.config import settings
from app.constants import DEF_INVEST_AMOUNT


class PreBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)


class ProjectDonationBase(Base):
    """Абстрактный класс для моделей CharityProject и Donation"""

    __abstract__ = True
    __table_args__ = (
        CheckConstraint(
            'full_amount > 0',
            name='check_pos_full_amount',
        ),
        CheckConstraint(
            'full_amount >= invested_amount',
            name='check_full_invest_amount',
        ),
    )
    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=DEF_INVEST_AMOUNT)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    def __repr__(self):
        if self.close_date:
            return (
                f"Объект {self.__class__.__name__}, закрыт {self.close_date}"
            )
        return f"Объект {self.__class__.__name__}. Общая сумма: {self.full_amount}. Текущая: {self.invested_amount}"


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


# Асинхронный генератор сессий.
async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
