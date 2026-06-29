## Useful commands

    View pods:
        kubectl get pods

    View deployments:
        kubectl get deployments

    View services:
        kubectl get services

    Describe a pod:
        kubectl describe pod <pod-name>

    View logs:
        kubectl logs <pod-name>

    Delete everything from a manifest:
        kubectl delete -f deployment.yaml

## Kubernetes with Docker running locally

Docker Compose and Kubernetes serve different purposes:

- Docker Compose orchestrates containers on a single machine.
- Kubernetes orchestrates containers across one or more machines, with features like scaling, rolling updates, and self-healing.

As we already have a docker-compose.yml for your FastAPI and React application, the typical migration is:

- Build your Docker images.
- Push them to a registry (or load them into Kind).
- Create Kubernetes Deployment and Service manifests for each component.
- Apply them with kubectl apply -f.

## Configure Kubernetes for CI-CD pipeline

1. Build and Push Docker Images

Backend:

    docker build -t bp-bedrock-hub/backend-python:1.0 .
    docker push bp-bedrock-hub/backend-python:1.0

Frontend:

    docker build -t bp-bedrock-hub/frontend-react:1.0 .
    docker push bp-bedrock-hub/frontend-react:1.0

2. Deploy namespace

    kubectl apply -f namespace.yaml

3. Apply backend service and deployment

    kubectl apply -f backend-deployment.yaml
    kubectl apply -f backend-service.yaml

4. Apply frontend service and deployment

    kubectl apply -f frontend-deployment.yaml
    kubectl apply -f frontend-service.yaml

5. Store secrets

    kubectl apply -f secret.yaml

6. Expose with Ingress

    kubectl apply -f ingress.yaml

7. Verify Deployment

    Check pods:
        kubectl get pods -n bp-bedrock-service

    Check services:
        kubectl get svc -n bp-bedrock-service

    Check ingress:
        kubectl get ingress -n bp-bedrock-service

    View logs:
        kubectl logs deployment/backend -n ai-cha

8. Deploy Automatically from GitHub Actions

    After your Docker images are pushed, add a deployment step:

        - name: Configure kubectl
        run: |
            mkdir -p ~/.kube
            echo "${{ secrets.KUBE_CONFIG }}" > ~/.kube/config

        - name: Deploy
        run: |
            kubectl apply -f k8s/

    Store your kubeconfig as a GitHub secret.

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Alternative to .github/workflows/docker.yml

- instead define .github/workflows/deploy.yml

- If unit tests are available then add the following into this ci workflow

    Refer to ci.yaml file in this folder
    and hence we achieve the workflow as follows

    For your FastAPI + React + Pinecone/OpenAI project, a good CI-CD flow is:

        Git Push
        ↓
        Backend Tests
        ↓
        Frontend Tests
        ↓
        Docker Build
        ↓
        Push Images
        ↓
        Deploy to Kubernetes



++++++++++++++++++++++++++++++++++++++++

A set of Kubernetes manifests created for the repo's components (backend, frontend, localstack) and a single Ingress (reverse-proxy) that routes /api → backend and / → frontend. 

Drop these into a k8s/manifests/ directory (or apply them with kubectl) — you still need to build/push the images and have an Ingress controller (e.g. nginx-ingress) installed in the cluster.

What is created (each block below is a separate YAML file):

    namespace.yaml — a namespace for the app
    backend-configmap.yaml — environment values from docker-compose (non-secret)
    backend-secret.yaml — placeholder for JWT_SECRET (create real secret before deploy)
    backend-deployment.yaml — Deployment for the Python backend
    backend-service.yaml — ClusterIP Service for backend
    frontend-deployment.yaml — Deployment for the React frontend
    frontend-service.yaml — ClusterIP Service for frontend
    localstack-deployment.yaml — Deployment for localstack (for dev/testing)
    localstack-service.yaml — ClusterIP Service for localstack
    ingress.yaml — Ingress resource routing /api to backend and / to frontend

Note: image names are placeholders — replace with your built image names (e.g., registry/bp-backend:tag). The frontend is configured to call the API at /api (so the browser-hosted frontend can call same-origin /api). If you prefer an nginx reverse-proxy Deployment instead of using a cluster Ingress resource, I can generate that as well.


## Next steps / notes:

Build and push images for backend and frontend and update the image fields in the Deployment manifests (I used placeholder names).

    Example: docker build -t your-registry/bp-backend:latest backend_python && docker push your-registry/bp-backend:latest

Create the Secret JWT_SECRET with kubectl (or replace stringData in backend-secret.yaml).
    kubectl apply -f backend-secret.yaml OR kubectl create secret generic backend-secret --from-literal=JWT_SECRET="your-secret" -n bp-bedrock

Install an Ingress controller (nginx ingress) in the cluster if not present (the manifests use ingressClassName: nginx).

Apply manifests:
    kubectl apply -f namespace.yaml
    kubectl apply -n bp-bedrock -f backend-configmap.yaml,backend-secret.yaml,backend-deployment.yaml,backend-service.yaml,frontend-deployment.yaml,frontend-service.yaml,localstack-deployment.yaml,localstack-service.yaml,ingress.yaml

    Note - with nginx-proxy, as below, you do not need the Ingress for external routing.

For production, consider:
Using PVCs instead of emptyDir for persistent storage.
Running localstack only for dev environments (omit in prod).
Adding liveness/readiness probes.
Securing secrets via a secret manager and imagePullSecrets if using private registries.
TLS for the Ingress (use cert-manager or cloud certificates).

## NGIX reverse proxy deployment manifests files

It has also generated an nginx reverse-proxy (ConfigMap + Deployment + Service) that will run inside the bp-bedrock namespace and route:

/api → backend:8000
/ → frontend:5173 It also forwards WebSocket/HMR upgrades so the Vite dev server (if you're using it) works through the proxy.

Apply these manifests in your cluster (they assume you already have the bp-bedrock namespace or the earlier namespace.yaml). If you prefer a NodePort instead of LoadBalancer, change the Service type.

Apply:
    kubectl apply -f nginx-configmap.yaml -n bp-bedrock
    kubectl apply -f nginx-deployment.yaml -n bp-bedrock
    kubectl apply -f nginx-service.yaml -n bp-bedrock

If you previously applied the Ingress, you can keep or remove it; 
with nginx-proxy you do not need the Ingress for external routing.

If you run the frontend as a static build served by nginx (recommended for production), you can instead build the frontend to static files and mount them into the nginx image (or build a custom image that serves static files), then adjust the nginx config to serve files directly rather than proxying to frontend:5173.

If running in cloud, the LoadBalancer service will provision an external IP; for bare-metal clusters, change Service type to NodePort and access via node:nodePort, or put a cloud load balancer in front.


