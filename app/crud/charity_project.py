from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_projects_by_completion_rate(
        self, session: AsyncSession
    ) -> list[dict]:
        objects = await session.execute(
            select(
                self.model.name,
                self.model.create_date,
                self.model.close_date,
                self.model.description,
            ).where(self.model.close_date != None)
        )

        projects = []

        for obj in objects.fetchall():
            tmp_project = {
                'name': obj['name'],
                'donation_timedelta': obj['close_date'] - obj['create_date'],
                'description': obj['description'],
            }
            projects.append(tmp_project)

        projects.sort(key=lambda project: project['donation_timedelta'])
        return projects


charityproject_crud = CRUDCharityProject(CharityProject)
