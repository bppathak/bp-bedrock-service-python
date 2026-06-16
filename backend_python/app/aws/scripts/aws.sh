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


# Create S3 bucket
    awslocal s3 mb s3://bedrock-prompts
    

# Create SQS
    awslocal sqs create-queue send-message request-queue

    poetry run awslocal sqs list-queues  # from the backend_python directory
    awslocal sqs list-queues

    awslocal sqs send-message \
        --queue-url http://localhost:4566/0000000000request-queue \
        --message-body '{"object_id":123"", "message": "Hello"}'    

# Create a table in dynmodb
    awslocal dyanmodb create-table \
        --table-name chat-history \
        --attribute-definitions \
            AttributeName=id,AttributeType=S \
        --key-schema \
            AttributeName=id,KeyType= HASH \
        --billing-mode PAY_PER_REQUEST

