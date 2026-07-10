cd backend-python
docker build -t bp-bedrock-hub/backend-python:1.0 .
docker push bp-bedrock-hub/backend-python:1.0

cd ../frontend-react
docker build -t bp-bedrock-hub/frontend-react:1.0 .
docker push bp-bedrock-hub/frontend-react:1.0

kubectl get pods
kubectl get deployments
kubectl get services

kubectl rollout status deployment/bp-bedrock

# Rollback to previous version if needed
# kubectl rollout undo deployment/bp-bedrock