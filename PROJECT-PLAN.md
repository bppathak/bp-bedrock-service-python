# AWS Bedrock Submission MVP Task List

## Summary
Create an MVP that lets a user complete a sequential React submission journey, persist each step to a Python/FastAPI backend, store metadata in DynamoDB, upload PDF files to S3, queue submitted files through SQS, and convert PDFs to TIFF via a worker/Lambda-style process.

## Backend Tasks
- Fix backend app wiring so FastAPI starts cleanly, including removing or replacing the missing `app.routes.items` import and registering real API routers.
- Define shared Pydantic models for users, submissions, presenter details, payment, form type, file metadata, statuses, and conversion status.
- Implement `GET /bp-api/healthcheck`.
- Implement auth endpoints:
  - `POST /bp-api/auth/register`
  - `POST /bp-api/auth/login`
  - `POST /bp-api/auth/refresh`
  - `POST /bp-api/auth/logout`
  - `POST /bp-api/auth/forgot-password`
  - `POST /bp-api/auth/reset-password`
- Implement JWT access tokens and refresh-token handling.
- Implement DynamoDB repository/service layer for users and submissions.
- Implement submission endpoints:
  - `POST /bp-api/submission/new`
  - `PUT /bp-api/submission/{id}/payment`
  - `PUT /bp-api/submission/{id}/formType`
  - `PUT /bp-api/submission/{id}/files`
  - `PUT /bp-api/submission/{id}`
  - `GET /bp-api/submission/{id}`
- Ensure every successful frontend step can create or update the current submission record.
- Implement `GET /bp-api/forms` with an initial static list of supported form types.
- Implement S3 upload support for PDF files, storing `submission_id`, `file_id`, original filename, size, and S3 object key in DynamoDB.
- Implement `POST /bp-api/events/submissions/{submission_id}/files/{file_id}` to update converted file metadata after TIFF conversion.
- Implement `/queue-file` or align it to the submission submit flow so records marked `SUBMITTED` are sent to SQS.
- Implement SQS message producer and consumer contract with `submission_id`, `file_id`, source PDF S3 key, and target TIFF location.
- Implement PDF-to-TIFF conversion worker/Lambda-compatible module.
- Store converted TIFF output in S3 and update DynamoDB conversion status to `CONVERTED` or `FAILED`.

## Frontend Tasks
- Replace local-only wizard state with API-backed submission state.
- Create a frontend API client with base URL configuration for local Docker and dev mode.
- Update the sequential pages to map to the required submission fields:
  - Presenter/contact details
  - Payment reference
  - Form type
  - PDF file upload
  - Review/submit
- On the first step, call `POST /bp-api/submission/new` and persist the returned submission ID.
- On each Next action, call the matching backend update endpoint before moving forward.
- Upload selected PDF files to the backend instead of only logging them in the browser.
- On final submit, set submission status to `SUBMITTED` and show clear success/error states.
- Add loading, validation, retry/error messages, and disabled states for users with fatigue or brain fog.
- Fix current TypeScript issues in page imports/types and remove unsafe casts where possible.
- Add Tailwind CSS setup or decide to keep current CSS if Tailwind is out of MVP scope.

## Docker & AWS Local Tasks
- Fix `docker-compose.yml` LocalStack service typo from `lamdba` to `lambda`.
- Add required environment variables for AWS region, LocalStack endpoint, S3 bucket, DynamoDB table names, SQS queue URL/name, JWT secrets, and CORS origins.
- Add startup/bootstrap scripts to create local DynamoDB tables, S3 buckets, and SQS queues.
- Ensure backend container can connect to LocalStack.
- Ensure frontend container can call backend via the correct Docker/dev URL.
- Add one-command local startup documentation.

## Test Plan
- Backend unit tests for Pydantic validation, submission status transitions, auth token handling, and repository logic.
- Backend API tests for all listed endpoints using FastAPI test client.
- LocalStack integration tests for DynamoDB writes, S3 upload metadata, SQS queue messages, and conversion-status updates.
- Frontend build test with `npm run build`.
- Frontend flow test for creating a submission, updating each step, uploading a PDF, and submitting.
- Docker smoke test confirming frontend, backend, LocalStack, healthcheck, and local AWS resources start together.

## Assumptions
- MVP status flow will use `OPEN -> SUBMITTED -> PROCESSING -> ACCEPTED/REJECTED`, with file-level conversion status using `WAITING -> QUEUED -> CONVERTED/FAILED`.
- Converted TIFF files should be stored in S3, while DynamoDB stores metadata and object references.
- Auth is part of the implementation backlog, but the first usable submission flow can be developed with a temporary/mock presenter if needed.
- LocalStack is the local AWS target for development and testing.
