import base64
import json

from model.common import BasicAuthCredentials


def basic_auth_handler(event, context):
    """
    This function processes the event when a certain lambda function is invoked,
    specifically handling those events that includes basic auth authorizer such as api docs.

    :param event: The event data.
    :type event: dict

    :param context: The context data.
    :type context: dict

    :return: The generated policy for the IAM or an unauthorized response.
    :rtype: dict
    """
    __ = context
    authorization_header = event["authorizationToken"]
    auth_type, encoded_credentials = authorization_header.split(None, 1)
    if auth_type != "Basic":
        return unauthorized_response("Unauthorized")

    decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
    username, password = decoded_credentials.split(":")

    if username == BasicAuthCredentials.username.value and password == BasicAuthCredentials.password.value:
        return generate_policy("user", "Allow", event["methodArn"])

    return unauthorized_response("Unauthorized")


def generate_policy(principal_id, effect, resource):
    """
    Generates an AWS IAM policy.

    :param principal_id: The principal ID.
    :type principal_id: str

    :param effect: The effect of the policy (e.g., 'Allow' or 'Deny').
    :type effect: str

    :param resource: The resource to which the policy applies.
    :type resource: str

    :return: The generated IAM policy.
    :rtype: dict
    """
    policy = {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [{"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}],
        },
    }
    return policy


def unauthorized_response(message):
    """
    Creates an unauthorized response for HTTP requests.

    :param message: The message to include in the response.
    :type message: str

    :return: The unauthorized response.
    """
    response = {
        "statusCode": 401,
        "body": json.dumps({"message": message}),
        "headers": {"WWW-Authenticate": "Basic"},
    }
    return response
