from datetime import datetime
from typing import Union, Optional

from app.models import CharityProject, Donation


def exc_status_note(obj: Union[CharityProject, Donation]) -> None:
    """
    Установка значений fully_invested и close_date, при
    достижения invested_amount значения равному в full_amount
    как в пожертвованиях так и в проектах.
    """

    if obj.full_amount == obj.invested_amount:
        obj.fully_invested = True
        obj.close_date = datetime.now()


def investing(
    target: Union[CharityProject, Donation],
    sources: Optional[Union[list[CharityProject], list[Donation]]],
) -> Union[list[CharityProject], list[Donation]]:
    """
    Ребалансировка значений атрибутов в записях объектов CharityProject, Donation.
    Процесс инвестирования.
    Если создан новый проект, а в базе были «свободные» (не распределённые по
    проектам) суммы пожертвований — они автоматически должны инвестироваться
    в новый проект. То же касается и создания пожертвований: если в момент
    пожертвования есть открытые проекты, эти пожертвования должны автоматически зачислиться на их счета.
    """

    invest_remeins: int = target.full_amount

    for cur_obj in sources:
        amount: int = cur_obj.full_amount - cur_obj.invested_amount

        if not invest_remeins:
            break

        if invest_remeins > amount:
            invest_remeins -= amount
            cur_obj.invested_amount += amount

        else:
            cur_obj.invested_amount += invest_remeins
            invest_remeins = 0

        exc_status_note(cur_obj)

    target.invested_amount = target.full_amount - invest_remeins
    exc_status_note(target)
    return sources
