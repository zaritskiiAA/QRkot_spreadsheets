from fastapi import APIRouter, Depends, Body

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.investment import investing
from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.crud.charity_project import charityproject_crud
from app.schemas.donation import DonationCreate, DonationtDB
from app.models import User


router = APIRouter()


@router.post(
    '/',
    response_model=DonationtDB,
    response_model_exclude_none=True,
    response_model_exclude={
        'user_id',
        'invested_amount',
        'fully_invested',
        'close_date',
    },
)
async def create_donation(
    donation: DonationCreate = Body(
        examples={
            'create': {
                'summary': 'Создание пожертвования',
                'description': 'Создавать может любой авторизированный пользователь',
                'value': {'full_amount': 300, 'comment': 'I generous uncle'},
            }
        }
    ),
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    new_donation = await donation_crud.create(donation, session, user)
    open_charities = await charityproject_crud.get_open_objects(session)
    modify = investing(new_donation, open_charities)
    await donation_crud.refresh([new_donation] + modify, session)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationtDB],
    dependencies=[Depends(current_superuser)],
)
async def get_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """Только суперпользователь может просматривать все пожертвования"""

    donations = await donation_crud.get_multi(session)
    return donations


@router.get(
    '/my',
    response_model=list[DonationtDB],
    response_model_exclude_none=True,
    response_model_exclude={
        'user_id',
        'invested_amount',
        'fully_invested',
        'close_date',
    },
)
async def get_my_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Любой авторизированный пользователь может просматривать собственные пожертвования."""

    my_donations = await donation_crud.get_object_by_attr(
        'user_id', user.id, session
    )
    return my_donations
