# Serverless Load Testing Framework
This repository contains code for a serverless API load test framework built using Step Functions that invoke Lambda functions using a fan-out design pattern that you can deploy using the SAM CLI. It includes the following files and folders:
- functions - Code for the application's Lambda functions to create and delete test users, and trigger authorized requests for API Gateway endpoint.
- statemachine - Definition for the state machine that orchestrates the load testing workflow.
- layers/python - Python library shared across Lambda functions

This example creates a Stepfunction workflow that sets up the infrastructure for running a load test with Cognito users against an API Gateway endpoint that is configured to use Cognito authorizer.

AWS Step Functions lets you coordinate multiple AWS services into serverless workflows so you can build and update apps quickly. Using Step Functions, you can design and run workflows that stitch together services, such as AWS Lambda, AWS Fargate, and Amazon SageMaker, into feature-rich applications.

The application uses several AWS resources, including Step Functions state machines, Lambda functions, Cognito user pool and Secrets manager. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Build

You would need the following tools installed in your IDE (Integrated Development Environment) before proceeding further:
- AWS SAM CLI
- Python 3.7

To build your application run the following command in your shell:

```bash
sam build
```

## Deploy

Run the following command to package and deploy the application to AWS, with a series of prompts. When prompted for apiGatewayUrl, provide the API Gateway URL route you intend to load test.

```bash
sam deploy --guided
```

After the stack creation is complete, you should see UserPoolID and AppClientID in the outputs section.

## Update API Gateway

- Navigate to the API Gateway console and choose the HTTP API you intend to load test. 
- Choose Authorization and select the authenticated route configured with a JWT authorizer.
- Choose Edit Authorizer and update the IssuerURL with Amazon Cognito user pool ID and audience app client ID with the corresponding values from the stack output section in previous steps
- Set authorization scope to aws.cognito.signin.user.admin

## Running the load test
- Open the Step Functions console and choose the state machine named apiloadtestCreateUsersAndFanOut-xxx.
- Choose Start Execution and provide the following JSON input. Configure the number of users for the load test and the number of calls per user:
    {
        "users": {
          "NumberOfUsers": "100",
          "NumberOfCallsPerUser": "100"
        }  
    }
- After the execution, you see the status updated to Succeeded

## Checking the load test results
- Navigate to API Gateway service within the console, choose Monitor → Logging, select the $default stage, and choose the Select button.
- Choose View Logs in CloudWatch to navigate to the CloudWatch Logs service, which loads the log group and displays the most recent log streams.
- Choose the "View in Logs Insights" button to navigate to the Log Insights page and visualize various metrics.

## Cleanup 
- To delete Amazon Cognito users, run the Step Functions workflow apiloadtestDeleteTestUsers. Provide the following input JSON with the same number of users that you created earlier:
   {
      "NumberOfUsers": "100"
    }
- Step Functions invokes the cleanUpTestUsers Lambda function. It is configured with the test Amazon Cognito user pool ID and app client ID environment variables created during the stack deployment. The users are deleted from the test user pool. 
- The Lambda function also schedules the corresponding KMS keys for deletion after seven days, the minimum waiting period.
- After the state machine is finished, navigate to Cognito → Manage User Pools → apiloadtest-loadtestidp → Users and Groups. Refresh the page to confirm that all users are deleted.
- To delete all the resources permanently and stop incurring cost, navigate to the CloudFormation console, select aws-apiloadtest-framework stack, and choose Delete → Delete stack.




