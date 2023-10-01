import os
import base64
import hashlib
import hmac

from boto3.session import Session
import logging


class Utils:
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

    @staticmethod
    def strip_error_message(message: str):
        return message.split(': ')[-1]
