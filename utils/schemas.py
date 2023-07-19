from typing import Optional
from datetime import datetime, date
from pydantic import BaseModel


class User(BaseModel):
    id: int
    birth_day: str
    ntrp: str
    first_name: str
    last_name: str
    tennis_experience: str
    phone_number: str
    user_name: str
    description: str

    class Config:
        orm_mode = True


class Booking(BaseModel):
    id: int
    court_id: int
    start_time: datetime
    end_time: datetime
    type: str
    # date: date
    additional_member: str
    created_at: datetime
    # user_id: int
    user: Optional[User]

    class Config:
        orm_mode = True
