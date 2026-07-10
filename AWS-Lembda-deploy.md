## Deploy Lambda into localstack

1. Create Your Lambda Function using JAVA

    mvn clean package

2. Create an IAM Role (Dummy Role)

LocalStack does not validate IAM permissions strictly, but Lambda requires a role ARN.

awslocal iam create-role \
  --role-name lambda-role \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{
      "Effect":"Allow",
      "Principal":{"Service":"lambda.amazonaws.com"},
      "Action":"sts:AssumeRole"
    }]
  }'

  OR simply use
    arn:aws:iam::000000000000:role/lambda-role

3. Create the Lambda Function in AWS, for JAVA

    awslocal lambda create-function \
        --function-name hello-java \
        --runtime java21 \
        --handler com.example.Handler::handleRequest \
        --zip-file fileb://target/my-app.jar \
        --role arn:aws:iam::000000000000:role/lambda-role


    aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name hello-go \
    --runtime provided.al2023 \
    --handler bootstrap \
    --zip-file fileb://function.zip \
    --role arn:aws:iam::000000000000:role/lambda-role

4. Verify Deployment

    List functions:

        awslocal lambda list-functions

    Get details:

        awslocal lambda get-function \
            --function-name hello-java

5. Invoke the Lambda

    awslocal lambda invoke \
    --function-name hello-java \
    response.json

    View output:

        cat response.json

    Expected:

        "Hello from LocalStack!"

6. Update the Function on AWS

    After rebuilding:

    awslocal lambda update-function-code \
        --function-name hello-java \
        --zip-file fileb://function.zip

## 6a. Deploy Using AWS CLI Instead of awslocal

Equivalent command:

    aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name hello-java \
    --runtime provided.al2023 \
    --handler bootstrap \
    --zip-file fileb://function.zip \
    --role arn:aws:iam::000000000000:role/lambda-role

7. Check Logs

    Follow LocalStack logs:

        docker logs -f localstack

    Or if running with Docker Compose:

        docker compose logs -f localstack

## FOR Python

        see .../app/aws/lambda/lambda_function.py

    and compressed this function
            zip function.zip lambda_function.py

    Compressed

    Update
        awslocal lambda update-function-code \
    --function-name hello-python \
    --zip-file fileb://function.zip

    Invoke

            lambda_functionawslocal lambda invoke \
                --function-name hello-python \
                --payload '{"name":"John"}' \
                response.json

        Output:

        {
        "statusCode": 200,
        "body": "Hello John!"
        }

    check logs
        docker logs -f localstack