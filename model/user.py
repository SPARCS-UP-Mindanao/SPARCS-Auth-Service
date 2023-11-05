from typing import Optional

from pydantic import BaseModel, EmailStr, Extra, Field


class SignUp(BaseModel):
    class Config:
        extra = Extra.forbid

    email: EmailStr = Field(..., title="Email")
    password: str = Field(..., title="Password")


class SignUpResponse(BaseModel):
    class Config:
        extra = Extra.ignore

    email: EmailStr = Field(..., title="Email")
    sub: str = Field(..., title="Sub", description="The unique identifier for the user.")


class ConfirmSignUp(BaseModel):
    class Config:
        extra = Extra.forbid

    email: EmailStr = Field(..., title="Email")
    confirmationCode: str = Field(..., title="Confirmation Code")


class Login(SignUp):
    class Config:
        extra = Extra.forbid


class RefreshTokenRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    sub: str = Field(..., title="User Sub")
    refreshToken: str = Field(..., title="Refresh Token")


class LogOutRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    accessToken: str = Field(..., title="Access Token")


class AuthResponse(BaseModel):
    class Config:
        extra = Extra.ignore

    accessToken: str = Field(..., title="Access Token")
    expiresIn: int = Field(..., title="Expires In")
    tokenType: str = Field(..., title="Token Type")
    refreshToken: Optional[str] = Field(None, title="Refresh Token")
    idToken: str = Field(..., title="Id Token")
    session: Optional[str] = Field(None, title="Session")
    sub: str = Field(..., title="Sub", description="The unique identifier for the user.")


class ForgotPasswordRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    email: EmailStr = Field(..., title="Email")


class ConfirmForgotPasswordRequest(SignUp):
    class Config:
        extra = Extra.forbid

    confirmationCode: str = Field(..., title="Confirmation Code")


class ChangePasswordRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    accessToken: str = Field(..., title="Access Token")
    previousPassword: str = Field(..., title="Previous Password")
    proposedPassword: str = Field(..., title="Proposed Password")


class UpdateTemporaryPasswordRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    email: EmailStr = Field(..., title="Email")
    prevPassword: str = Field(..., title="Previous Password")
    newPassword: str = Field(..., title="Password")


class Challenge(BaseModel):
    class Config:
        extra = Extra.forbid

    challengeName: str = Field(..., title="Challenge Name")
    session: str = Field(..., title="SessionId")
