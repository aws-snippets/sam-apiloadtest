import json
import boto3
import os
import logging
import lambda_shared as layer
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
cognitoClient = boto3.client('cognito-idp')
clientId = os.environ['client_id']
poolId = os.environ['userpool_id']
NUMBER_OF_USERS = 10

def deleteSecret(userName):
    try:
        secret = layer.SecretsManagerSecret(boto3.client('secretsmanager'))
        secret.setName(userName)
        secret.delete(True)
    except Exception as e:
        print("ExceptionSecret exception for {} {}".format(userName, e))


def deleteSpecifiedUsers(numberOfUsers):
    for i in range(0, numberOfUsers, 1):
        userName = 'loadtestuser'+str(i)
        try:
            cognitoClient.admin_delete_user(
                UserPoolId=poolId,
                Username=userName)
                
            deleteSecret(userName)
            print("Deleted user {} {}. Continuing".format(userName, poolId))
        except Exception as e:
            print("Failed deleting user {}. Continuing".format(userName))

def lambda_handler(event, context):
    numberOfUsers = int(event['NumberOfUsers'] or NUMBER_OF_USERS)
    deleteSpecifiedUsers(numberOfUsers)

    return numberOfUsers
        