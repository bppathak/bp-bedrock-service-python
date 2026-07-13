# Load the image
docker save python-backend:latest -o python-backend.tar
docker save react-frontend:latest -o react-frontend.tar
# Import images
docker exec -i desktop-control-plane ctr -n k8s.io images import - < python-backend.tar
docker exec -i desktop-control-plane ctr -n k8s.io images import - < react-frontend.tar
# Verify
docker exec desktop-control-plane ctr -n k8s.io images ls | grep python
# Restart the pod
kubectl delete pod -n bp-bedrock -l app=backend
kubectl delete pod -n bp-bedrock -l app=frontend
# Delete generated tar files
rm python-backend.tar react-frontend.tar