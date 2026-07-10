#!/bin/bash

## Installing and configuring awslocal / aws 

poetry add --group dev awscli-local
# find ~/.local -name awslocal
poetry run awslocal --version
    aws-cli/2.33.0 Python/3.9.25 Linux/5.14.0-611.54.1.el9_7.x86_64 source/x86_64.rhel.9

# Test Mock AWS running
        curl https://localhost:4566/_localstack/health

ALTERNATIVELY,
    Use aws instead of awslocal, as below, with same effect

        bash-5.1$ aws --endpoint-url=http://localhost:4566 sqs list-queues

    You must specify a region. You can also configure your region by running "aws configure".

    bash-5.1$ aws configure
        AWS Access Key ID [None]: 
        AWS Secret Access Key [None]: 
        Default region name [None]: eu-west-2
        Default output format [None]: json


# Using awslocal for localstack

Services available on lambda
    curl http://localhost:4566/_localstack/health



# Create S3 bucket
    awslocal s3 mb s3://bedrock-prompts

    aws --endpoint-url=http://localhost:4566 s3 ls
    aws --endpoint-url=http://localhost:4566 s3api list-buckets
    

# Create SQS
    awslocal sqs create-queue send-message request-queue

    poetry run awslocal sqs list-queues  # from the backend_python directory
    awslocal sqs list-queues

    awslocal sqs send-message \
        --queue-url http://localhost:4566/0000000000request-queue \
        --message-body '{"object_id":123"", "message": "Hello"}'    


    Queue Statistics
        awslocal sqs get-queue-attributes \
            --queue-url http://sqs.eu-west-2.localhost.localstack.cloud:4566/000000000000/bp-submission-conversion-queue \
            --attribute-names All

# Create a table in dynmodb
    awslocal dyanmodb create-table \
        --table-name chat-history \
        --attribute-definitions \
            AttributeName=id,AttributeType=S \
        --key-schema \
            AttributeName=id,KeyType= HASH \
        --billing-mode PAY_PER_REQUEST


    aws --endpoint-url=http://localhost:4566 dynamodb list-tables

    awslocal dynamodb get-item \
      --table-name Users \
      --key '{"userId":{"S":"1"}}'


## Lambda

    awslocal lambda create-function \
        --function-name my-function \
        --runtime python3.9 \
        --role arn:aws:iam::000000000000:role/lambda-role \
        --handler lambda_function.lambda_handler \
        --zip-file fileb://function.zip 

    aws --endpoint-url=http://localhost:4566 lambda list-functions

    aws --endpoint-url=http://localhost:4566 lambda get-function \
        --function-name my-function

    awslocal lambda invoke \
        --function-name my-function \
        response.json

    With a payload:

    awslocal lambda invoke \
        --function-name my-function \
        --payload '{"name":"John"}' \
        response.json


## Docker useful commands

    docker ps -a
    docker stop <container_id>
    docker start <container_id>
    docker exec -it <container_id> bash
    docker logs <container_id>  

    docker logs -f localstack : for continuous logs

    To inspect the environnment variables of a running container:
        docker exec -it <container_id> env

    docker system df

    Remove everything un-used

        docker system prune -a

        docker system prune -a --volumes
        (This is the most aggressive cleanup command and can free a lot of space.)



