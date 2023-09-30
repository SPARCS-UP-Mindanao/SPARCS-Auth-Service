import base64
import hashlib
import hmac
import logging
import os
from http import HTTPStatus

from boto3 import client as boto3_client
from boto3.session import Session
from starlette.responses import JSONResponse

from model.user import (
    AuthResponse,
    ConfirmSignUp,
    Login,
    RefreshTokenRequest,
    SignUp,
    SignUpResponse,
)


class AuthUsecase:
    def __init__(self) -> None:
        self.client = boto3_client('cognito-idp', region_name=os.environ['REGION'])
        self.user_pool_id = os.getenv('USER_POOL_ID')
        self.user_pool_client_id = os.getenv('USER_POOL_CLIENT_ID')
        self.client_secret = self.get_secret(os.getenv('CLIENT_SECRET_NAME'))

    @staticmethod
    def get_secret(secret_name: str) -> str:
        secret = ''
        try:
            session = Session()
            client = session.client(service_name='ssm', region_name=os.getenv('REGION'))
            resp = client.get_parameter(Name=secret_name, WithDecryption=True)
            secret = resp['Parameter']['Value']
        except Exception as e:
            message = f'Failed to get secret, {secret_name}, from AWS SSM: {str(e)}'
            logging.error(message)

        return secret

    @staticmethod
    def compute_secret_hash(client_secret, user_name, client_id):
        message = user_name + client_id
        dig = hmac.new(
            bytes(client_secret, 'latin-1'), msg=bytes(message, 'latin-1'), digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()

    def signup(self, sign_up_details: SignUp):
        try:
            auth_response = self.client.sign_up(
                ClientId=self.user_pool_client_id,
                Username=sign_up_details.email,
                Password=sign_up_details.password,
                SecretHash=self.compute_secret_hash(
                    client_secret=self.client_secret,
                    user_name=sign_up_details.email,
                    client_id=self.user_pool_client_id,
                ),
            )
            sub = auth_response['UserSub']
            res = SignUpResponse(
                email=sign_up_details.email,
                sub=sub,
            )
        except Exception as e:
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})
        else:
            return res

    def confirm_signup(self, confirm_signup: ConfirmSignUp):
        try:
            self.client.confirm_sign_up(
                SecretHash=self.compute_secret_hash(
                    client_secret=self.client_secret,
                    user_name=confirm_signup.email,
                    client_id=self.user_pool_client_id,
                ),
                Username=confirm_signup.email,
                ClientId=self.user_pool_client_id,
                ConfirmationCode=confirm_signup.confirmationCode,
            )
        except Exception as e:
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "User confirmed successfully",
                },
            )

    def login(self, login_details: Login):
        try:
            response = self.client.initiate_auth(
                ClientId=self.user_pool_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': login_details.email,
                    'PASSWORD': login_details.password,
                    'SECRET_HASH': self.compute_secret_hash(
                        client_secret=self.client_secret,
                        user_name=login_details.email,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )
            auth_result = response.get('AuthenticationResult', {})
            return AuthResponse(
                accessToken=auth_result.get('AccessToken'),
                expiresIn=auth_result.get('ExpiresIn'),
                tokenType=auth_result.get('TokenType'),
                refreshToken=auth_result.get('RefreshToken'),
                idToken=auth_result.get('IdToken'),
            )
        except Exception as e:
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})

    def refresh(self, refresh_token_request: RefreshTokenRequest):
        try:
            response = self.client.initiate_auth(
                ClientId=self.user_pool_client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token_request.refreshToken,
                    'SECRET_HASH': self.compute_secret_hash(
                        client_secret=self.client_secret,
                        user_name=refresh_token_request.sub,
                        client_id=self.user_pool_client_id,
                    ),
                },
            )
            auth_result = response.get('AuthenticationResult', {})
            return AuthResponse(
                accessToken=auth_result.get('AccessToken'),
                expiresIn=auth_result.get('ExpiresIn'),
                tokenType=auth_result.get('TokenType'),
                refreshToken=auth_result.get('RefreshToken'),
                idToken=auth_result.get('IdToken'),
            )
        except Exception as e:
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})

    def sign_out(self, accessToken: str):
        try:
            self.client.global_sign_out(AccessToken=accessToken)
        except Exception as e:
            return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"message": str(e)})
        else:
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "User logged out successfully",
                },
            )
