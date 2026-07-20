# Overview

We're building aws bedrock application for storing a submission with converting a pdf file, uploaded, into tiff format with the following components
- Frontend
- Backend
- dockerise build and deployment

The MVP needs to be simple enough that someone with brain fog or fatigue can use it quickly, but powerful enough to surface useful insights over time.

# Frontend 
- It will consist few pages in sequentials order to store submission data on each page

# Backend
-  This service has the following feature fo
        - Storing Submission Data in the aws dynamoDB
        - And convering a pdf file, as part of submission data, into tiff file.
    - provide few endpoints to create/update and delete submission data in dynamoDB
        Every click on frontend updates insert/update data in the database
        Once frontend capture all the data, including the pdf file to convert, status of the data is changed to "READY TO SUBMIT"
    - S3 bucket : Provide feature of inserting pdf file into s3 bucket and store submission_id & s3 image_id into dynamoDB
        This also updates the submissioni data with updating status as READY TO SUBMIT
    - SQS : Provide feature of running SQS pick up the message once the submission is markted as READY TO SUBMIT status
        The endpoint is marked as /queue-file
    - Lembda: Provide feature of Lambda, which keep looking with time interval for files available to convert into tiff on SQS 
        Lamdba, convert pdf file in to 
        store tiff file into the database with establishing the link with original pdf file.


# Data Models

Users / Presenter
- id (UUID)
- email (unique)
- password_hash
- display_name
- timezone (default UTC)
- create_at
- last_updated_at

Submission Schema
​ {​ 
    "id": "string",​ 
    "create_at": "timestamp",​ 
    "last_modified_at": "timestamp",​ 
    "status": "OPEN|SUBMITTED|PROCESSING|SENT_TO_EXTERNALSYSTEM|ACCEPTED|REJECTED"​ 
    "presenter": {​ 
        "email": "string",​ 
    },
    ​"payment_reference": "string"​ 
    "form": {​ 
        "form_type": "string",​ 
        "file_details": [ {​ "form_id": "string", 
        "file_name": "string" 
        "file_size": "long" 
        "converted_file_id": "string"​ 
        "conversion_status": "WAITING|QUEUED|CONVERTED|FAILED",​ 
        "last_modifield_at": "timestamp"​ 
        } ]​
    }​
 }

# API Endpoints

Auth
    POST /bp-api/auth/register
    POST /bp-api/auth/login
    POST /bp-api/auth/refresh
    POST /bp-api/auth/logout
    POST /bp-api/auth/forgot-password
    /bp-api/auth/reset-password

Submissions

    POST /bp-api/submission/new : Create a new Submissions which will be included the presenter email address This will return the id of the new submission

    PUT /bp-api/submission/{id}/payment : Sets the payment details

    PUT /bp-api/submission/{id}/formType : Sets the form type of the submission

    PUT /bp-api/submission/{id}/files : Adds metadata for each file to the submission

    PUT /bp-api/submission/{id} : Sets the submission-status to SUBMITTED This means submission is finally submitted with all required data from web, i.e web journey ended.

    GET /bp-api/submission/{id} : Get a submission based on an id

Forms

    GET /bp-api/forms : Get a list of all submittable forms

Events

    No Events identified yet but may include third party interfaces such as aws sqs or RabbitMQ integration etc

File Transfer

    POST /bp-api/events/submissions/{submission_id}/files/{file_id} : Update metadata for file attached to submission with a reference to the location of the converted file in S3 bucket (object ID) 
    Note - file to be received in pdf format

Others

    GET /bp-api/healthcheck : Get an api Healthcheck endpoint

# Core Features

Submission

# Tech Stack
- Frontend : React, Vite with Typescript, Taiwind CSS
- Backend : Python
- Database : AWS dynamoDB
- Auth: JWT with refresh tokens
- Hosting: TBD (Vercel, Railway, or Render)
- Logging - Apache slf4k
- AWS
    Hosting
    Simple Queue Service
    S3 (via file-transfer-api)
    Lembda

