#!/bin/bash

set -e

echo "======================================"
echo "Setting up kubernetesenvironment"
echo "./start-k8s.sh my-namespace"
echo "======================================"

if [ -z "$1" ]; then
    echo "****Parameter is null or empty****"
    # exit 1
else
    echo "Parameter value is: $1"
fi

NAMESPACE="${1:-bp-bedrock}"
echo "Using namespace: $NAMESPACE"

BACKEND_IMAGE="python-backend:latest"
FRONTEND_IMAGE="react-frontend:latest"
LOCALSTACK_IMAGE="localstack/localstack:latest"
IMAGE_MISSING=false

# ./cleanup-environment.sh $NAMESPACE

# echo "Starting Docker..."
# ./start-bedrock-docker.sh

docker build -t python-backend:latest ./backend_python
docker build -t react-frontend:latest ./frontend_react
docker pull localstack/localstack:3.0.2

echo "Checking Docker images..."
for IMAGE in "$BACKEND_IMAGE" "$FRONTEND_IMAGE" "$LOCALSTACK_IMAGE"; do
    if docker image inspect "$IMAGE" >/dev/null 2>&1; then
        echo "Image exists: $IMAGE"
    else
        echo "Image missing: $IMAGE"
        IMAGE_MISSING=true
    fi
done

if [ "$IMAGE_MISSING" = true ]; then
    echo "Building Docker images..."
    docker compose build
else
    echo "All images already exist. Skipping build."
fi

echo "Checking Kubernetes connectivity..."
docker context show
kubectl config set-context --current --namespace=$NAMESPACE

if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "ERROR: Kubernetes cluster is not available."
    echo "Start Docker Desktop and wait until Kubernetes is Running."
    exit 1
fi

echo "Checking Kubernetes cluster..."
until kubectl get nodes >/dev/null 2>&1
do
    echo "Waiting for Kubernetes..."
    sleep 5
done


echo "Applying namespace..."
kubectl apply -f k8s/manifests/namespace.yaml

echo "Waiting for namespace $NAMESPACE..."
until kubectl get namespace $NAMESPACE >/dev/null 2>&1
do
    echo "Waiting..."
    sleep 3
done

echo "Applying Kubernetes manifests..."
kubectl apply -f ./k8s/manifests
echo "Waiting for manifests to be applied..."
sleep 30

echo "update dynamodb, s3 and sqs endpoints in localstack"
kubectl apply -f ./k8s/localstack-init.yaml

kubectl get pods -n $NAMESPACE

echo "Importing docker images to kubernetes"
./import-dockerImage-2-k2s.sh

#echo "Applying bootstrap localstack..."
#./bootstrap-localstack.sh

echo "Done."