import base64
import json

from model.common import BasicAuthCredentials


def basic_auth_handler(event, context):
    """
    This function processes the event when a certain lambda function is
    invoke that includes basic auth authorizer such as api docs
    """
    __ = context
    authorization_header = event['authorizationToken']
    auth_type, encoded_credentials = authorization_header.split(None, 1)
    if auth_type != 'Basic':
        return unauthorized_response('Unauthorized')

    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
    username, password = decoded_credentials.split(':')

    if username == BasicAuthCredentials.username.value and password == BasicAuthCredentials.password.value:
        return generate_policy('user', 'Allow', event['methodArn'])

    return unauthorized_response('Unauthorized')


def generate_policy(principal_id, effect, resource):
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{'Action': 'execute-api:Invoke', 'Effect': effect, 'Resource': resource}],
        },
    }
    return policy


def unauthorized_response(message):
    response = {'statusCode': 401, 'body': json.dumps({'message': message}), 'headers': {'WWW-Authenticate': 'Basic'}}
    return response
