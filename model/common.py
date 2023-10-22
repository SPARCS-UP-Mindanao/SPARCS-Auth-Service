from enum import Enum

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class BasicAuthCredentials(Enum):
    username: str = 'sparcs'
    password: str = 'sparcs_events_123!'
