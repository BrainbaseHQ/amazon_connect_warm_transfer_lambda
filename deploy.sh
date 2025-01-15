#!/usr/bin/env bash
set -e

AWS_ACCOUNT_ID="<YOUR_AWS_ACCOUNT_ID>"
AWS_REGION="<YOUR_AWS_REGION>"
ECR_REPO_NAME="amazon_connect_warm_transfer_lambda"
IMAGE_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest"

echo "=== Building Docker Image (amd64 only) ==="
docker buildx build \
  --platform=linux/amd64 \
  --load \
  -t ${ECR_REPO_NAME}:latest \
  .

echo "=== Authenticating to ECR ==="
aws ecr get-login-password --region ${AWS_REGION} | \
  docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "=== Tagging Docker Image ==="
docker tag ${ECR_REPO_NAME}:latest ${IMAGE_URI}

echo "=== Pushing Docker Image to ECR ==="
docker push ${IMAGE_URI}


# echo "=== Updating Lambda to use the new Container Image ==="
# aws lambda update-function-code \
#   --function-name ${LAMBDA_FUNCTION_NAME} \
#   --image-uri ${IMAGE_URI}

echo "=== Deployment Complete! ==="
