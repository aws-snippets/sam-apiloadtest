import json
import boto3
import os
import logging
import urllib3
import lambda_shared as layer
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
cognitoClient = boto3.client('cognito-idp')
clientId = os.environ['client_id']
poolId = os.environ['userpool_id']
api_url = os.environ['api_url']
NUMBER_OF_CALLS_PER_USER = 10

def getPassword(userName):
    try:
        secret = layer.SecretsManagerSecret(boto3.client('secretsmanager'))
        secret.setName(userName)
        value = secret.get_value()
        return value['SecretString']
    except Exception as e:
        print("ExceptionSecret exception for {} {}".format(userName, e))

def triggerPerUserTest(userName, numberOfCallsPerUser):
    try:
        tokens = cognitoClient.admin_initiate_auth(
        UserPoolId=poolId,
        ClientId=clientId,
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            "USERNAME": userName,
            "PASSWORD": getPassword(userName)
        }
        )

        for i in range(1, numberOfCallsPerUser, 1):
            http = urllib3.PoolManager()
            https_response = http.request('GET',
                api_url,
                headers={'Content-Type': 'application/json', 'authorization': 'Bearer ' + tokens['AuthenticationResult']['AccessToken'], 'aud': clientId})
    except Exception as e:
        print("Load test failed for user {} {}. Continuing".format(userName, e))


def lambda_handler(event, context):
    numberOfCallsPerUser = int(event['NumberOfCallsPerUser'] or NUMBER_OF_CALLS_PER_USER)
    userName = event['UserName']
    
    triggerPerUserTest(userName, numberOfCallsPerUser)

    return {
        'status': 200
    }
