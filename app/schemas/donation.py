from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, Extra

from app.constants import GT_VALUE, DEF_INVEST_AMOUNT


class DonationBase(BaseModel):
    full_amount: int = Field(gt=GT_VALUE)
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    pass


class DonationtDB(DonationBase):
    id: int
    create_date: datetime
    user_id: int
    invested_amount: int = DEF_INVEST_AMOUNT
    fully_invested: bool = False
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
