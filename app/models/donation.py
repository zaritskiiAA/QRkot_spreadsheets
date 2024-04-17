from sqlalchemy import Column, Text, Integer, ForeignKey

from app.core.db import ProjectDonationBase


class Donation(ProjectDonationBase):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
