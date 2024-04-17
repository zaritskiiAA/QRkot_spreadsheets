from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charityproject_crud
from app.models import CharityProject


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
) -> None:
    project = await charityproject_crud.get_object_by_attr(
        'name', project_name, session
    )
    if project:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!',
        )


async def check_project_exists(
    project_id: int, session: AsyncSession
) -> CharityProject:
    project = await charityproject_crud.get(project_id, session)
    if not project:
        raise HTTPException(status_code=404, detail='Проект не найден')
    return project


async def check_lockup_update_fields(cur_amount: int, new_amount: int) -> None:
    if cur_amount > new_amount:
        raise HTTPException(
            status_code=422,
            detail='Нелья установить значение full_amount меньше уже вложенной суммы.',
        )


async def check_lockup_dfields_value(project: CharityProject) -> None:
    """Запрет на удаление полей с конкретным значением"""

    if project.invested_amount:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!',
        )


async def check_close_date_status(project) -> None:
    """Запрет на изменение завершенного проекта"""

    if project.close_date is not None:
        raise HTTPException(
            status_code=400,
            detail='Завершенный проект не подлежит корректировкам!',
        )
