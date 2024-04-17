from sqlalchemy import Column, Text, String

from app.core.db import ProjectDonationBase
from app.constants import MAX_LEN_NAME


class CharityProject(ProjectDonationBase):
    name = Column(String(MAX_LEN_NAME), unique=True, nullable=False)
    description = Column(Text, nullable=False)
