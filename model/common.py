from enum import Enum

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class BasicAuthCredentials(str, Enum):
    username: str = 'durianpy'
    password: str = 'durianpy_events_123!'
