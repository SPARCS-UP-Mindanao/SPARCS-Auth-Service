import base64
import hashlib
import hmac
import logging
import os

from boto3.session import Session


class Utils:
    @staticmethod
    def get_secret(secret_name: str) -> str:
        """
        Retrieve a secret from AWS Systems Manager Parameter Store.

        :param secret_name: The name of the secret to retrieve.
        :type secret_name: str

        :return: The retrieved secret value.
        :rtype: str
        """
        secret = ""
        try:
            session = Session()
            client = session.client(service_name="ssm", region_name=os.getenv("REGION"))
            resp = client.get_parameter(Name=secret_name, WithDecryption=True)
            secret = resp["Parameter"]["Value"]
        except Exception as e:
            message = f"Failed to get secret, {secret_name}, from AWS SSM: {str(e)}"
            logging.error(message)

        return secret

    @staticmethod
    def compute_secret_hash(client_secret, user_name, client_id):
        """
        Compute the secret hash for AWS Cognito authentication.

        :param client_secret: The client secret.
        :type client_secret: str

        :param user_name: The username.
        :type user_name: str

        :param client_id: The client ID.
        :type client_id: str

        :return: The computed secret hash.
        :rtype: str
        """
        message = user_name + client_id
        dig = hmac.new(
            bytes(client_secret, "latin-1"),
            msg=bytes(message, "latin-1"),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(dig).decode()

    @staticmethod
    def strip_error_message(message: str):
        """
        Strip the error message.

        :param message: The error message.
        :type message: str

        :return: The stripped error message.
        :rtype: str
        """
        return message.split(": ")[-1]
