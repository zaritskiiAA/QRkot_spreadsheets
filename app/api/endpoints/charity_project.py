from fastapi import APIRouter, Depends, Body

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_name_duplicate,
    check_project_exists,
    check_lockup_dfields_value,
    check_lockup_update_fields,
    check_close_date_status,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charityproject_crud
from app.crud.donation import donation_crud
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate,
    CharityProjectDB,
)
from app.services.investment import exc_status_note, investing

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charityproject(
    project: CharityProjectCreate = Body(
        examples={
            'create': {
                'summary': 'Создание проекта',
                'description': 'Создавать может только суперюзер',
                'value': {
                    'name': 'For homeless cat',
                    'description': 'for cats',
                    'full_amount': 300,
                },
            }
        }
    ),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров. Вызывает процесс инвестирования
    см. README.MD github.com/aleksanderZaritskiy/cat_charity_fund

    """

    await check_name_duplicate(project.name, session)

    new_project = await charityproject_crud.create(project, session)
    open_donations = await donation_crud.get_open_objects(session)
    modify = investing(new_project, open_donations)
    await charityproject_crud.refresh([new_project] + modify, session)
    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
)
async def get_charityproject(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Просмотр всех проектов доступ любому пользователю,
    в т.ч. и неавторизированному
    """
    all_projects = await charityproject_crud.get_multi(session)
    return all_projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def partial_update_charityproject(
    project_id: int,
    obj_in: CharityProjectUpdate = Body(
        examples={
            'update_name': {
                'summary': 'Изменение имени',
                'description': 'Изменять может только суперюзер',
                'value': {
                    'name': 'For homeless dogs',
                },
            },
            'update_desc': {
                'summary': 'Изменение описания',
                'description': 'Изменять может только суперюзер',
                'value': {
                    'description': 'for dogs',
                },
            },
            'update_full_amount': {
                'summary': 'Изменение общей суммы пожертвований',
                'description': 'Изменять может только суперюзер. На значение >= текущему пожертвованию',
                'value': {
                    'full_amount': 777,
                },
            },
        }
    ),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров. Вызывает процесс инвестирования
    см. README.MD github.com/aleksanderZaritskiy/cat_charity_fund

    """

    project = await check_project_exists(project_id, session)
    await check_close_date_status(project)
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount:
        await check_lockup_update_fields(
            project.invested_amount, obj_in.full_amount
        )
    project = await charityproject_crud.update(project, obj_in, session)
    exc_status_note(project)
    await charityproject_crud.refresh(project, session)
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def delete_charityproject(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров. Удалять можно проекты, которые ещё не успели собрать пожертвования
    и не имею статус fully_invested = True
    """

    project = await check_project_exists(project_id, session)
    await check_lockup_dfields_value(project)
    await check_close_date_status(project)
    project = await charityproject_crud.remove(project, session)
    return project
