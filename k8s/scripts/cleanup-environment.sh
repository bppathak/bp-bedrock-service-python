#!/bin/bash

set -e

echo "======================================"
echo "Cleaning up environment"
echo "./cleanup-environment.sh my-namespace"
echo "======================================"

echo "This script will clean docker containers and all images"
echo "This will clean the kubernetesnamespace, if exists: ${#1}"
echo "One important point: if Docker Desktop Kubernetes is enabled, "
echo "======================================"
echo "it is normal to still see some Kubernetes system images afterward."
echo "Those belong to Docker Desktop itself and will come back automatically."
echo "======================================"

if [ -z "$1" ]; then
    echo "*****Parameter is null or empty*****"
    # exit 1
else
    echo "Parameter value is: $1"
fi

NAMESPACE="${1:-bp-bedrock}"
echo "*******************************"
echo "Using namespace: $NAMESPACE"
kubectl config set-context --current --namespace=$NAMESPACE
kubectl config view --minify
echo "*******************************"

echo "======================================"
echo "Stopping and cleaning Docker resources"
echo "======================================"

# Stop all running containers
if [ "$(docker ps -q)" ]; then
    echo "Stopping running containers..."
    docker stop $(docker ps -q)
else
    echo "No running containers found."
fi

echo "Running Docker cleanup..."
docker system prune -a --volumes -f

# IMAGES=$(docker images -aq)
# if [ -n "$IMAGES" ]; then
#    docker rmi -f $IMAGES
# else
#     echo "No images found"
# fi

echo "======================================"
echo "Cleaning Kubernetes namespace"
echo "======================================"

# Delete Kubernetes namespace if it exists
if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
    echo "Deleting namespace: $NAMESPACE"
    kubectl delete namespace "$NAMESPACE"
else
    echo "Namespace $NAMESPACE ******DOES NOT EXIST.******  "
    # echo "Kubernetes namespaces:"
    # kubectl get namespaces
fi

echo "======================================"
echo "Verifying cleanup"
echo "======================================"

echo "Docker containers:"
docker ps -a

echo "Docker images:"
docker images

echo "Cleanup completed successfully including k2s namespace: $NAMESPACE."