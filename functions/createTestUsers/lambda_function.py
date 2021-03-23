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

def getPassword(userName):
    try:
        secret = layer.SecretsManagerSecret(boto3.client('secretsmanager'))
        secret.create(userName, secret.get_random_password(20))
    except Exception as e:
        print("ExceptionSecret exception for {} {}".format(userName, e))
    finally:
        secret.setName(userName)
        value = secret.get_value()
        return value['SecretString']
        
def deleteSecret(userName):
    try:
        secret = layer.SecretsManagerSecret(boto3.client('secretsmanager'))
        secret.setName(userName)
        secret.delete(True)
    except Exception as e:
        print("ExceptionSecret exception for {} {}".format(userName, e))


def createUsers(i, userNames):
    try:
        userName = 'loadtestuser'+str(i)
        password = getPassword(userName)
        userNames.append(userName)
    
        response = cognitoClient.sign_up(
            ClientId=clientId,
            Username=userName,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': 'Client'+str(i)+'@octank.com'
                },
            ]
        )

        response = cognitoClient.admin_confirm_sign_up(
            UserPoolId=poolId,
            Username=userName
        )
    
        response = cognitoClient.admin_set_user_password(
            UserPoolId=poolId,
            Username=userName,
            Password=password,
            Permanent=True
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            logger.info("Username {} already exists".format(userName))
        else:            
            print("Exception for user {}, {}".format(userName, e))
        

def setupUsers(numberOfUsers, userNames):
    for i in range(0, int(numberOfUsers), 1):
        createUsers(i, userNames)

def lambda_handler(event, context):
    userNames = []
    setupUsers(int(event['NumberOfUsers'] or NUMBER_OF_USERS), userNames)

    return event
        