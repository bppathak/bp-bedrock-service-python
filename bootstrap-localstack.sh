#!/usr/bin/env bash
set -euo pipefail

AWS_ENDPOINT_URL="${AWS_ENDPOINT_URL:-http://localhost:4566}"
AWS_REGION="${AWS_DEFAULT_REGION:-eu-west-2}"
S3_BUCKET="${S3_BUCKET:-bp-submission-files}"
SQS_QUEUE_NAME="${SQS_QUEUE_NAME:-bp-submission-conversion-queue}"
DYNAMODB_SUBMISSIONS_TABLE="${DYNAMODB_SUBMISSIONS_TABLE:-bp-submissions}"
DYNAMODB_USERS_TABLE="${DYNAMODB_USERS_TABLE:-bp-users}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"

aws --endpoint-url "$AWS_ENDPOINT_URL" --region "$AWS_REGION" s3api create-bucket \
  --bucket "$S3_BUCKET" \
  --create-bucket-configuration LocationConstraint="$AWS_REGION" || true

aws --endpoint-url "$AWS_ENDPOINT_URL" --region "$AWS_REGION" sqs create-queue \
  --queue-name "$SQS_QUEUE_NAME" || true

aws --endpoint-url "$AWS_ENDPOINT_URL" --region "$AWS_REGION" dynamodb create-table \
  --table-name "$DYNAMODB_SUBMISSIONS_TABLE" \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST || true

aws --endpoint-url "$AWS_ENDPOINT_URL" --region "$AWS_REGION" dynamodb create-table \
  --table-name "$DYNAMODB_USERS_TABLE" \
  --attribute-definitions AttributeName=email,AttributeType=S \
  --key-schema AttributeName=email,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST || true

echo "LocalStack resources are ready."
