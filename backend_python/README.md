# Service Description

This service has the following feature fo
    - Storing Submission Data in the database
    - And convering a pdf file, as part of submission data, into tiff file.

- provide few endpoints to store submission data in dynamoDB
    Every click on frontend updates insert/update data in the database
    Once frontend capture all the data, including the pdf file to convert, status of the data is changed to "READY TO SUBMIT"
- S3 bucket : Provide feature of inserting pdf file into s3 bucket and store submission_id & s3 image_id into dynamoDB
    This also updates the submissioni data with updating status as READY TO SUBMIT
- SQS : Provide feature of running SQS pick up the message once the submission is markted as READY TO SUBMIT status
    The endpoint is marked as /queue-file
- Lembda: Provide feature of Lambda, which keep looking with time interval for files available to convert into tiff on SQS 
    Lamdba, convert pdf file in to 
    store tiff file into the database with establishing the link with original pdf file.

# List of Endpoints

    Create Submission
    Delete Submission


# How to Run

    Run docker to start and stop the services
        ./start-bedrock-docker-start.sh and ./stop-bedrock.docker.start.sh

        Docker will run the following three services
            backend-python
            frontend-react
            localstack : AWS mock
    
    Individual services can also be run, for debug purpose as
        ./start-backend.sh : for backend service
        ./stop-frontend.sh : for frontend service

# Misc

    bash-5.1$ poetry add --group dev awscli-local
        Using version ^0.22.2 for awscli-local

        Updating dependencies
        Resolving dependencies... (2.1s)

        Package operations: 9 installs, 0 updates, 0 removals

        - Installing six (1.17.0)
        - Installing jmespath (1.1.0)
        - Installing python-dateutil (2.9.0.post0)
        - Installing urllib3 (2.7.0)
        - Installing botocore (1.43.29)
        - Installing s3transfer (0.18.0)
        - Installing boto3 (1.43.29)
        - Installing localstack-client (2.11)
        - Installing awscli-local (0.22.2)

        Writing lock file
        bash-5.1$ awslocal --version