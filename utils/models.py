import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import select
from sqlalchemy import Column, String, Integer, BigInteger

from utils.database import Base


class UserOrm(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": "api"}
    id: Mapped[int] = mapped_column(primary_key=True)
    birth_day = Column(String)
    ntrp = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    tennis_experience = Column(String)
    phone_number = Column(String)
    user_name = Column(String)
    description = Column(String)
    # bookings = relationship("Booking", back_populates="user")

    def __repr__(self):
        return f'User(id={self.id!r}, name={self.first_name!r}, surname={self.last_name!r})'

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class BookingOrm(Base):
    __tablename__ = 'booking'
    __table_args__ = {"schema": "api"}
    id: Mapped[int] = mapped_column(primary_key=True)
    court_id = Column()
    start_time = Column()
    end_time = Column()
    date = Column()
    type = Column()
    additional_member = Column()
    created_at = Column()
    user_id = Column()
    # user_id = Column(ForeignKey("users.id"))

    def __repr__(self):
        # if self.user_id:
        #     return f'Booking(id={self.id!r}, name={self.first_name!r}, surname={self.last_name!r})'
        return f'Booking(id={self.id!r})'

    def to_json(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    def get_future_bookings(cls, days_depth: int = 0) -> list['BookingOrm']:
        """Список будущих бронирований"""
        today = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).date()
        last_date = today + datetime.timedelta(days=days_depth)
        if not days_depth:
            return select(cls).where(today < cls.start_time)
        return select(cls).where((today < cls.start_time) & (cls.start_time < last_date))