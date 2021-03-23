import json
import boto3

NUMBER_OF_USERS = 1000
NUMBER_OF_CALLS_PER_USER = 100


def setupUsers(numberOfUsers, numberOfCallsPerUser, userNames):
    for i in range(0, int(numberOfUsers), 1):
        userName = 'loadtestuser'+str(i)
        userNames.append({"UserName": userName, "NumberOfCallsPerUser": numberOfCallsPerUser})

def lambda_handler(event, context):
    userNames = []
    setupUsers(int(event['NumberOfUsers'] or NUMBER_OF_USERS), int(event['NumberOfCallsPerUser'] or NUMBER_OF_CALLS_PER_USER), userNames)

    return {
        'statusCode': 200,
        'userNames': userNames
    }
        