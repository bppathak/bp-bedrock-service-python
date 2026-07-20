# BP Bedrock Submission Service

MVP for a sequential submission journey that stores submission data, uploads PDF files, queues conversion work, and records TIFF conversion metadata.

## Stack

- Frontend: React, Vite, TypeScript
- Backend: Python, FastAPI, Pydantic
- Local AWS: LocalStack for S3, SQS, DynamoDB
- Conversion worker: Lambda-compatible Python module at `backend_python/app/worker/pdf_to_tiff.py`

## Run Locally

Use Scripts
    ./start-backend.sh
    ./start-frontend.sh

    if using docker
        ./start-bedrock-docker.sh
        ./stop-bedrock-docker.sh

    For kubernetes deployment, look at ./documents/Readme-kubernetes.sh

Alternatively, we can also Start the application:

```bash
docker compose up --build
```

In another terminal, create the LocalStack resources:

```bash
./bootstrap-localstack.sh
```

Open:

- Frontend: http://localhost:5173
- Backend healthcheck: http://localhost:8000/bp-api/healthcheck

## Important Environment Variables

- `AWS_DEFAULT_REGION`: AWS region, default `eu-west-2`
- `AWS_ENDPOINT_URL`: LocalStack endpoint, default `http://localstack:4566` in Docker
- `S3_BUCKET`: PDF/TIFF object bucket
- `SQS_QUEUE_NAME`: conversion queue name
- `SQS_QUEUE_URL`: conversion queue URL
- `DYNAMODB_SUBMISSIONS_TABLE`: submissions table name
- `DYNAMODB_USERS_TABLE`: users table name
- `JWT_SECRET`: local JWT signing secret
- `CORS_ORIGINS`: comma-separated allowed frontend origins
- `VITE_API_BASE_URL`: browser-facing backend URL

## MVP Flow

1. Create a submission with presenter details.
2. Save payment reference.
3. Save form type.
4. Upload a PDF.
5. Submit the record, which marks files as `QUEUED` and sends a conversion message to SQS or the local queue fallback.
6. The worker converts the source PDF to TIFF and updates conversion metadata through the same service layer.

## Useful Commands

Backend tests:

```bash
cd backend_python
pytest
```

Frontend build:

```bash
cd frontend_react
npm run build
```
