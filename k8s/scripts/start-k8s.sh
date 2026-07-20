#!/bin/bash

set -e

K8_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "======================================"
echo "K8 home: $K8_HOME"
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
echo "====================================="
echo "Using namespace: $NAMESPACE"
echo "====================================="

BACKEND_IMAGE="python-backend:latest"
FRONTEND_IMAGE="react-frontend:latest"
LOCALSTACK_IMAGE="localstack/localstack:latest"
IMAGE_MISSING=false

# ./cleanup-environment.sh $NAMESPACE

# echo "Starting Docker..."
# ./start-bedrock-docker.sh

docker build -t python-backend:latest $K8_HOME/../../backend_python
docker build -t react-frontend:latest $K8_HOME/../../frontend_react
# docker pull localstack/localstack:3.0.2

echo "====================================="
echo "Checking Docker images..."
echo "====================================="
for IMAGE in "$BACKEND_IMAGE" "$FRONTEND_IMAGE" "$LOCALSTACK_IMAGE"; do
    if docker image inspect "$IMAGE" >/dev/null 2>&1; then
        echo "Image exists: $IMAGE"
    else
        echo "Image missing: $IMAGE"
        IMAGE_MISSING=true
    fi
done

if [ "$IMAGE_MISSING" = true ]; then
    echo "====================================="
    echo "Building Docker images..."
    echo "====================================="
    docker compose build
else
    echo "====================================="
    echo "All Docker images already exist. Skipping build."
    echo "====================================="
fi

echo "======================================"
echo "Checking Kubernetes connectivity..."
echo "======================================"
docker context show
kubectl config set-context --current --namespace=$NAMESPACE

if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "======================================"
    echo "ERROR: Kubernetes cluster is not available."
    echo "Start Docker Desktop and wait until Kubernetes is Running."
    echo "======================================"
    exit 1
fi

echo "======================================"
echo "Checking Kubernetes cluster..."
echo "======================================"
until kubectl get nodes >/dev/null 2>&1
do
    echo "Waiting for Kubernetes..."
    sleep 5
done

echo "======================================"
echo "Applying namespace..."
echo "======================================"
kubectl apply -f $K8_HOME/../../k8s/manifests/namespace.yaml

echo "======================================"
echo "Waiting for namespace $NAMESPACE..."
echo "======================================"
until kubectl get namespace $NAMESPACE >/dev/null 2>&1
do
    echo "Waiting..."
    sleep 3
done

echo "======================================"
echo "Applying Kubernetes manifests..."
kubectl apply -f $K8_HOME/../../k8s/manifests
echo "Waiting for manifests to be applied..."
sleep 30

echo "======================================"
echo "update dynamodb, s3 and sqs endpoints in localstack"
echo "======================================"
kubectl apply -f $K8_HOME/../../k8s/localstack-init.yaml

kubectl get pods -n $NAMESPACE

echo "======================================"
echo "Importing docker images to kubernetes"
echo "======================================"
$K8_HOME/../../k8s/scripts/import-dockerImage-2-k2s.sh

echo "All successfully Done."