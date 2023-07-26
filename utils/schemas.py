from __future__ import annotations
from typing import Optional

from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, constr


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    birth_day: str
    ntrp: str
    first_name: str
    last_name: str
    tennis_experience: str
    phone_number: str
    user_name: Optional[str]
    description: Optional[str]


class Booking(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    court_id: int
    start_time: datetime
    end_time: datetime
    type: str
    # date: date
    additional_member: str
    created_at: datetime
    # user_id: int
    user: Optional[User] = None

