from pydantic import BaseModel, Extra, Field


class SignUp(BaseModel):
    class Config:
        extra = Extra.forbid

    username: str = Field(..., title="Username")
    password: str = Field(..., title="Password")
    email: str = Field(..., title="Email")


class ConfirmSignUp(BaseModel):
    class Config:
        extra = Extra.forbid

    username: str = Field(..., title="Username")
    confirmation_code: str = Field(..., title="Confirmation Code")


class Login(BaseModel):
    class Config:
        extra = Extra.forbid

    username: str = Field(..., title="Username")
    password: str = Field(..., title="Password")


class RefreshTokenRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    username: str = Field(..., title="Username")
    refresh_token: str = Field(..., title="Refresh Token")
