from pydantic import BaseModel, Extra, Field


class SignUp(BaseModel):
    class Config:
        extra = Extra.forbid

    email: str = Field(..., title="Email")
    password: str = Field(..., title="Password")


class SignUpResponse(BaseModel):
    class Config:
        extra = Extra.ignore

    email: str = Field(..., title="Email")
    sub: str = Field(..., title="Sub", description="The unique identifier for the user.")


class ConfirmSignUp(BaseModel):
    class Config:
        extra = Extra.forbid

    email: str = Field(..., title="Email")
    confirmationCode: str = Field(..., title="Confirmation Code")


class Login(BaseModel):
    class Config:
        extra = Extra.forbid

    email: str = Field(..., title="Email")
    password: str = Field(..., title="Password")


class RefreshTokenRequest(BaseModel):
    class Config:
        extra = Extra.forbid

    sub: str = Field(..., title="Email")
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
    refreshToken: str = Field(..., title="Refresh Token")
    idToken: str = Field(..., title="Id Token")
