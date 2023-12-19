from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from constants.common_constants import EmailType


class EmailIn(BaseModel):
    to: Optional[List[EmailStr]] = Field(None, title="Email address of the recipient")
    cc: Optional[List[EmailStr]] = Field(None, title="CC Email addresses")
    bcc: Optional[List[EmailStr]] = Field(None, title="BCC Email address")
    subject: str = Field(..., title="Subject of the email")
    salutation: str = Field(..., title="Salutation of the email")
    body: List[str] = Field(..., title="Body of the email")
    regards: List[str] = Field(..., title="Regards of the email")
    emailType: EmailType = Field(None, title="Type of the email")
    eventId: str = Field(None, title="Event ID of the email")
