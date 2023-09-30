import os
import hmac
import hashlib
import base64
from starlette.responses import JSONResponse
from boto3 import client as boto3_client
from model.user import SignUp, Login, RefreshTokenRequest, ConfirmSignUp


class AuthUsecase:
    def __init__(self) -> None:
        self.client = boto3_client('cognito-idp', region_name=os.environ['REGION'])
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.user_pool_client_id = os.getenv('USER_POOL_CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')

    @staticmethod
    def compute_secret_hash(client_secret, username, client_id):
        message = username + client_id
        dig = hmac.new(
            bytes(client_secret, 'latin-1'), msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    def signup(self, sign_up_details: SignUp):
        try:
            response = self.client.sign_up(
                ClientId=self.user_pool_client_id,
                Username=sign_up_details.username,
                Password=sign_up_details.password,
                UserAttributes=[
                    {'Name': 'email', 'Value': sign_up_details.email},
                ],
                SecretHash=self.compute_secret_hash(
                    client_secret=self.client_secret,
                    username=sign_up_details.username,
                    client_id=self.user_pool_client_id,
                ),
            )
        except Exception as e:
            return JSONResponse(status_code=400, content={"message": str(e)})
        else:
            return response

    def confirm_signup(self, confirm_signup: ConfirmSignUp):
        try:
            response = self.client.confirm_sign_up(
                SecretHash=self.compute_secret_hash(
                    client_secret=self.client_secret,
                    username=confirm_signup.username,
                    client_id=self.user_pool_client_id,
                ),
                Username=confirm_signup.username,
                ClientId=self.user_pool_client_id,
                ConfirmationCode=confirm_signup.confirmation_code,
            )
        except Exception as e:
            return JSONResponse(status_code=400, content={"message": str(e)})
        else:
            return response

    def login(self, login_details: Login):
        try:
            response = self.client.initiate_auth(
                ClientId=self.user_pool_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': login_details.username,
                    'PASSWORD': login_details.password,
                    'SECRET_HASH': self.compute_secret_hash(
                        client_secret=self.client_secret,
                        username=login_details.username,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )
        except Exception as e:
            return JSONResponse(status_code=400, content={"message": str(e)})
        else:
            return response

    def refresh(self, refresh_token_request: RefreshTokenRequest):
        try:
            response = self.client.initiate_auth(
                ClientId=self.user_pool_client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token_request.refresh_token,
                    'SECRET_HASH': self.compute_secret_hash(
                        client_secret=self.client_secret,
                        username=refresh_token_request.username,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )
        except Exception as e:
            return JSONResponse(status_code=400, content={"message": str(e)})
        else:
            return response

    def sign_out(self, access_token: str):
        try:
            return self.client.global_sign_out(AccessToken=access_token)
        except Exception as e:
            return JSONResponse(status_code=400, content={"message": str(e)})
