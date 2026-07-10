[TOC]



Introduction
​	Cluster : Created by Kubernetes

​	User can create for specific deployments

​			Namespace : 
​			Pod : 
​			Service:
​			Deployment: 

# Enable Kubernetes in Docker Desktop

bhupendrapathak@MacBookPro bp-bedrock-service-python % kubectl --context=docker-desktop get nodes

NAME             STATUS   ROLES           AGE   VERSION

docker-desktop   Ready    control-plane   8d    v1.24.0



bhupendrapathak@MacBookPro bp-bedrock-service-python % kubectl config view --raw -o jsonpath='{.clusters[?(@.name=="docker-desktop")].cluster.server}'

https://kubernetes.docker.internal:6443**%**

# Build the Docker images

- Clone the repository
- Run docker compose

Since Docker Desktop and Kubernetes share the same Docker image store, you usually **do not need to push the images to a registry**.

NOTE - If there are separate Dockerfiles:

```
docker build -t my-frontend:latest ./frontend
docker build -t my-backend:latest ./backend
```

# Check the Kubernetes manifests

## check docker image

​	docker images

## Update manifest files

`Deployment` should reference the same image names you just built.

Example:

```
spec:
  containers:
    - name: backend
      image: my-backend:latest
      imagePullPolicy: Never
```

If the image exists locally, set:

```
imagePullPolicy: Never
```

or

```
imagePullPolicy: IfNotPresent
```

Otherwise Kubernetes may try to pull the image from Docker Hub.



# Deploy the manifests



## Apply namespace

Try applying the namespace first:

```
kubectl apply -f k8s/manifests/namespace.yaml
```

Verify it exists:

```
kubectl get namespaces
```

You should see:

```
bp-bedrock
```

## Apply remaining manifests

If they are in a directory:

```
kubectl apply -f k8s/
```

or individually:

```
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

# Verify everything

Pods:

```
kubectl get pods -n bp-bedrock
```

Services:

```
kubectl get services -n bp-bedrock
```

Deployments:

```
kubectl get deployments -n bp-bedrock
```

# Check logs

kubectl logs deployment/backend -n bp-bedrock

kubectl get pods -n bp-bedrock | grep nginx

kubectl exec -it nginx-proxy-7cf7cc84d6-chsww -n bp-bedrock -- sh

wget -qO- http://backend:8000/openapi.json

Restart nginx in ConfigMaps

​		kubectl rollout restart deployment nginx-proxy -n bp-bedrock

If a pod isn't starting:

```
kubectl get pods -n bp-bedrock
kubectl logs <pod-name> -f
```
Describe the pod:

```
kubectl describe pod <pod-name>
```

These commands are the quickest way to identify image, networking, or configuration issues.


## Log Files

To temporarily using our namespace and not the default

- kubectl config set-context --current --namespace=bp-bedrock
  - Context "docker-desktop" modified.
  - kubectl get namespaces                                     

​				NAME              STATUS   AGE

​				bp-bedrock        Active   26m
​				default           Active   16d
​				kube-node-lease   Active   16d
​				kube-public       Active   16d
​				kube-system       Active   16d

**If using default namespace**

bhupendrapathak@MacBookPro bp-bedrock-service-python % kubectl get pods -n bp-bedrock

NAME                           READY   STATUS    RESTARTS   AGE

backend-fc85d9ccc-4gqxr        1/1     Running   0          21m
backend-fc85d9ccc-tlfzf        1/1     Running   0          21m
frontend-5fb596ccd9-tmm4x      1/1     Running   0          21m
frontend-5fb596ccd9-vw22l      1/1     Running   0          21m
localstack-74c4b9fc8-x6mgt     1/1     Running   0          21m
nginx-proxy-855d7d67f6-5hk7k   1/1     Running   0          21m
nginx-proxy-855d7d67f6-8d9ln   1/1     Running   0          21m

​	kubectl describe pod backend-fc85d9ccc-4gqxr -n bp-bedrock
​	kubectl logs deployment/nginx-proxy -n bp-bedrock

# Access the application

If you created a `NodePort` service:

```
kubectl get svc
```

You'll see a port similar to:

```
backend-service   NodePort   ...   8080:30080/TCP
```

Access it at:

```
http://localhost:30080
```

If you created a `LoadBalancer` service in Docker Desktop, it is typically available via `localhost` as well.


# Summary

## If your application depends on LocalStack

You have two options:

- **Run LocalStack as another Kubernetes Deployment and Service**, so your backend connects to `http://localstack:4566`.
- **Continue running LocalStack with Docker Compose**, and configure your backend to reach it using an appropriate endpoint. Note that a pod's `localhost` is the pod itself, not your host machine or another container.

## Recommended project layout



```
project/
├── backend/
│   ├── Dockerfile
│   └── ...
├── frontend/
│   ├── Dockerfile
│   └── ...
├── k8s/
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-service.yaml
│   └── localstack-deployment.yaml   (optional)
└── docker-compose.yml               (for local development)
```



This lets you use:

- **Docker Compose** for local development.
- **Kubernetes manifests** for running the application in Docker Desktop Kubernetes.

If you're having trouble deploying, I can also review your `deployment.yaml` and `service.yaml` files to check for common issues such as incorrect image names, `imagePullPolicy`, service selectors, or port mappings.



# Misc kubectl Commands



kubectl config view

kubectl config view --minify

bhupendrapathak@MacBookPro bp-bedrock-service-python % dig https://devkops1.service.np.iptho.co.uk

; <<>> DiG 9.10.6 <<>> https://devkops1.service.np.iptho.co.uk

;; global options: +cmd

;; Got answer:

;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 38904

;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 1, ADDITIONAL: 1



;; OPT PSEUDOSECTION:

; EDNS: version: 0, flags:; udp: 1220

;; QUESTION SECTION:

;https://devkops1.service.np.iptho.co.uk. IN A



;; AUTHORITY SECTION:

service.np.iptho.co.uk.	7	IN	SOA	ns-1355.awsdns-41.org. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400



;; Query time: 14 msec

;; SERVER: 192.168.0.1#53(192.168.0.1)

;; WHEN: Mon Jun 29 16:23:35 BST 2026

;; MSG SIZE  rcvd: 153

------



bhupendrapathak@MacBookPro bp-bedrock-service-python % kubectl config get-contexts              

CURRENT   NAME             CLUSTER          AUTHINFO         NAMESPACE

\*         docker-desktop   docker-desktop   docker-desktop   

​          sst1             devkops1         devkops1         ho-it-sst1-i-cw-cwi

​          sst2             devkops1         devkops1         ho-it-sst2-i-cw-cwi

​          sst3             devkops1         devkops1         ho-it-sst3-i-cw-cwi

​          sst4             devkops1         devkops1         ho-it-sst4-i-cw-cwi

​          sst5             devkops1         devkops1         ho-it-sst5-i-cw-cwi

​          sst6             devkops1         devkops1         ho-it-sst5-i-cw-cwi



bhupendrapathak@MacBookPro bp-bedrock-service-python % kubectl config use-context docker-desktop

Switched to context "docker-desktop".

------



# Generate a strong random JWT secret

On Linux or macOS:

```
openssl rand -base64 32
```



Example output:

```
8R2J0J7YQ+6Q8Q7xJq2u7v0m6x4xM4WnQfX4Yw3yGmA=
```



Create the secret:

```
kubectl create secret generic jwt-secret \
  --from-literal=JWT_SECRET="$(openssl rand -base64 32)"
```



------

## Verify the value (for testing)

To view the stored value:

```
kubectl get secret jwt-secret -o jsonpath='{.data.JWT_SECRET}'
```



It will be Base64 encoded. Decode it with:

```
kubectl get secret jwt-secret -o jsonpath='{.data.JWT_SECRET}' | base64 --decode
```



Using a Kubernetes Secret is preferable to hardcoding the JWT secret in your application or storing it in a ConfigMap, because Secrets are intended for sensitive values such as signing keys, passwords, and API tokens.



# Docker Commands



To stop and remove **all Docker containers and images** on your machine, use the following commands.

## Stop all running containers

```
docker stop $(docker ps -q)
```



If there are no running containers, you may see an empty argument error. You can ignore it.



## Remove all containers



```
docker rm $(docker ps -aq)
```



------

## Remove all images



```
docker rmi $(docker images -q)
```

If some images are in use, remove containers first (step 2).



## One command cleanup

To stop containers, remove containers, remove unused images, networks, and volumes:

```
docker system prune -a --volumes
```



You will be prompted:

```
Are you sure you want to continue? [y/N]
```

Enter:

```
y
```



------

## Verify cleanup

Containers:

```
docker ps -a
```



Images:

```
docker images
```



Both should be empty.



## For Docker Desktop Kubernetes

If you want to also remove Kubernetes resources you deployed:

```
kubectl delete namespace bp-bedrock
```



This removes:

- deployments
- pods
- services
- configmaps
- secrets
- other resources in that namespace

Then recreate when needed:

```
kubectl create namespace bp-bedrock
```

For your current setup (frontend, backend, LocalStack), `docker system prune -a --volumes` plus deleting the Kubernetes namespace will give you a clean reset.



# Error Handling

## Deployment Error Noticed 1



​	bhupendrapathak@MacBookPro bp-bedrock-service-python % kubectl get po

NAME                           READY   STATUS              RESTARTS   AGE

backend-6455cc4b77-cx7wx       0/1     ErrImageNeverPull   0          14s

backend-6455cc4b77-mj5ht       0/1     ErrImageNeverPull   0          14s

frontend-7c959d46c-d6vjj       0/1     ErrImageNeverPull   0          14s

frontend-7c959d46c-rdw8w       0/1     ErrImageNeverPull   0          14s

localstack-5bfdd7478-52r27     0/1     ContainerCreating   0          14s

nginx-proxy-7cf7cc84d6-b6gjg   1/1     Running             0          14s

nginx-proxy-7cf7cc84d6-g6w6n   1/1     Running             0          14s



## Solution:

Check the following commands to get the error details



​	kubectl describe pod backend-6455cc4b77-cx7wx -n bp-bedrock	

​	kubectl get deployment backend -n bp-bedrock -o yaml | grep image



Docker images are built correctly; they just need to be imported into the Kubernetes container runtime.

You **do have the image**:



```
python-backend:latest
```



in `docker images`, but your Kubernetes cluster **cannot see the image**.

This happens because newer Docker Desktop versions run Kubernetes using **containerd**, not the same Docker image store that `docker images` shows.

Your Docker CLI image exists here:



```
Docker image store
        |
        └── python-backend:latest
```



but Kubernetes is looking here:



```
Docker Desktop Kubernetes containerd image store
        |
        └── (python-backend:latest missing)
```



### Solution 1 (Recommended): Load the image into Kubernetes

First check if your Docker Desktop Kubernetes uses `kind`:



```
kubectl get nodes -o wide
```

You have:

```
desktop-control-plane
```

which indicates the Kubernetes node is using a kind-style container runtime.

Load your images:

```
docker save python-backend:latest -o python-backend.tar
docker save react-frontend:latest -o react-frontend.tar
```

Then import them into the Kubernetes node:

```
docker exec -i desktop-control-plane ctr -n k8s.io images import - < python-backend.tar
docker exec -i desktop-control-plane ctr -n k8s.io images import - < react-frontend.tar
```

Verify:

```
docker exec desktop-control-plane ctr -n k8s.io images ls | grep python
```

You should see:

```
python-backend:latest
```

Restart pods:

```
kubectl delete pod -n bp-bedrock -l app=backend
kubectl delete pod -n bp-bedrock -l app=frontend
```



------

### Solution 3: Push images to a registry

This is the production approach.

Tag:



```
docker tag python-backend:latest yourrepo/python-backend:latest
```



Push:



```
docker push yourrepo/python-backend:latest
```



Deployment:

```
image: yourrepo/python-backend:latest
imagePullPolicy: Always
```

------

### Also change your deployment

For local development, keep:

```
imagePullPolicy: IfNotPresent
```

instead of:

```
imagePullPolicy: Never
```

Example:

```
containers:
- name: backend
  image: python-backend:latest
  imagePullPolicy: IfNotPresent
```



`Never` is useful only when you are 100% sure the Kubernetes runtime already has the image.

------



# Kubectl deployment Error 2:



localstack-5bfdd7478-sddns     0/1     ContainerCreating   0          2m15s



Check for Localstack error under Event using the command

​	kubectl describe pod localstack-5bfdd7478-sddns -n bp-bedrock



## Solution:

The error is:

```
MountVolume.SetUp failed for volume "docker-sock" :
hostPath type check failed: /var/run/docker.sock is not a socket file
```

Your `localstack` pod is trying to mount:

```
/var/run/docker.sock
```

from the Kubernetes node into the container, but in your Docker Desktop Kubernetes environment that path **does not exist as a Docker socket**.

This is common when moving from Docker Compose to Kubernetes, especially with newer Docker Desktop versions using **containerd**.

------

### Why it happens

Your deployment probably has something like:

```
volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
      type: Socket
```

and:

```
volumeMounts:
  - name: docker-sock
    mountPath: /var/run/docker.sock
```

The `type: Socket` check requires the host path to be a real Unix socket. Kubernetes checks the node (`desktop-control-plane`), not your Mac filesystem.

------

### Solution 1: Remove the Docker socket mount (recommended)

For most LocalStack usage, you do **not need** Docker socket access.

Remove:



```
volumes:
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
      type: Socket
```



and remove:



```
volumeMounts:
  - name: docker-sock
    mountPath: /var/run/docker.sock
```



Then apply:



```
kubectl apply -f k8s/manifests/localstack.yaml -n bp-bedrock
```



Restart:



```
kubectl delete pod -n bp-bedrock -l app=localstack
```



------

### Solution 2: Change hostPath type (not usually needed)

You could change:



```
type: Socket
```



to:



```
type: Directory
```



but this will not help because `/var/run/docker.sock` is expected to be a socket, not a directory.

------

### Solution 3: If you specifically need Docker socket

Check whether Docker socket exists inside the Kubernetes node:



```
docker exec -it desktop-control-plane ls -l /var/run/
```



You would need to see:



```
srw-rw---- docker.sock
```



If it is missing, Kubernetes cannot mount it.

------

### LocalStack Kubernetes configuration

A typical LocalStack deployment does not need Docker socket:



```
containers:
- name: localstack
  image: localstack/localstack:3.0.2
  ports:
    - containerPort: 4566
  env:
    - name: SERVICES
      value: "s3,dynamodb,sqs,lambda"
```



No `docker.sock` volume required.

------

Given your setup:

- Docker Desktop Kubernetes
- containerd image store
- LocalStack running inside Kubernetes

I recommend removing the Docker socket mount. It is a Docker Compose pattern and usually should not be carried into Kubernetes.



# Proxy Error 3 : Nginx 



Unable to render this definition

The provided definition does not specify a valid version field.

Please indicate a valid Swagger or OpenAPI version field. Supported version fields are `swagger: "2.0"` and `openapi: 3.0.x`, `openapi: 3.1.x`, or `openapi: 3.2.x` (for example, `openapi: 3.2.0`).



## Solution

Behavior confirms the NGINX routing issue:

- `http://localhost/docs` → **frontend**
- `http://localhost/api/docs` → **Swagger UI loads but OpenAPI version error**

The backend is not being routed correctly for FastAPI Swagger.

FastAPI Swagger UI at `/docs` internally requests:

```
/openapi.json
```

When you access:

```
http://localhost/api/docs
```

Swagger tries to fetch:

```
/api/openapi.json
```

but your backend probably only exposes:

```
/openapi.json
```

You need to make NGINX rewrite the paths.





# Error 4: botocore.exceptions.NoCredentialsError 

The error is 

```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```



Backend pod is calling LocalStack, but **boto3 cannot find AWS credentials inside the Kubernetes container**.

LocalStack does not require real AWS credentials, but boto3 still requires credentials to sign requests.



## Solutions



## 1. Add AWS credentials to your backend Deployment

Update your backend deployment YAML:



```
env:
  - name: AWS_ACCESS_KEY_ID
    value: test

  - name: AWS_SECRET_ACCESS_KEY
    value: test

  - name: AWS_DEFAULT_REGION
    value: eu-west-2

  - name: AWS_REGION
    value: eu-west-2

  - name: AWS_ENDPOINT_URL
    value: http://localstack:4566
```



Example:



```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: bp-bedrock
spec:
  template:
    spec:
      containers:
        - name: backend
          image: python-backend:latest
          env:
            - name: AWS_ACCESS_KEY_ID
              value: test
            - name: AWS_SECRET_ACCESS_KEY
              value: test
            - name: AWS_REGION
              value: eu-west-2
            - name: AWS_ENDPOINT_URL
              value: http://localstack:4566
```



------

## 2. Apply the change



```
kubectl apply -f backend-deployment.yaml -n bp-bedrock
```



Restart the pods:



```
kubectl rollout restart deployment backend -n bp-bedrock
```



Check:



```
kubectl get pods -n bp-bedrock
```



------

## 3. Verify credentials inside the pod

After the pod restarts:



```
kubectl exec -it deployment/backend -n bp-bedrock -- sh
```



Run:



```
env | grep AWS
```



Expected:



```
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
AWS_REGION=eu-west-2
AWS_ENDPOINT_URL=http://localstack:4566
```



------

## 4. Make sure your boto3 client uses the endpoint

Your Python code should look like:



```
import boto3
import os

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
```

or:

```
dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localstack:4566",
    region_name="eu-west-2",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)
```



------



# Error 5: (ResourceNotFoundException) when calling the PutItem operation



The error is:

```
botocore.errorfactory.ResourceNotFoundException:
An error occurred (ResourceNotFoundException) when calling the PutItem operation:
Cannot do operations on a non-existent table
```

This means the backend successfully connected to LocalStack DynamoDB, but the table:

```
bp-submissions
```

does not exist in the LocalStack instance that your Kubernetes backend is using.



NOTE - If your LocalStack pod restarts and you do not have persistence configured, all tables disappear.

Also, note, we have define "bootstrap-localstack.sh" to populate dynamoDB table on localstack



## Solution: Create the table automatically

For Kubernetes, create a Kubernetes Job that runs after LocalStack starts.

Example:

```
apiVersion: batch/v1
kind: Job
metadata:
  name: dynamodb-init
  namespace: bp-bedrock
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: init
        image: amazon/aws-cli
        env:
        - name: AWS_ACCESS_KEY_ID
          value: test
        - name: AWS_SECRET_ACCESS_KEY
          value: test
        command:
        - sh
        - -c
        - |
          aws dynamodb create-table \
            --table-name bp-submissions \
            --attribute-definitions AttributeName=id,AttributeType=S \
            --key-schema AttributeName=id,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST \
            --endpoint-url http://localstack:4566 \
            --region eu-west-2
```

Then:

```
kubectl apply -f dynamodb-init.yaml
```



# Error 6 : NoSuchBucket

botocore.errorfactory.NoSuchBucket: An error occurred (NoSuchBucket) when calling the PutObject operation: The specified bucket does not exist

This error is the S3 equivalent of the DynamoDB table error you fixed earlier.

```
botocore.errorfactory.NoSuchBucket:
The specified bucket does not exist
```

## Solution

Application Bucket name - bp-submission-files



### 1- List existing buckets

From the backend pod:

```
kubectl exec -it deployment/backend -n bp-bedrock -- sh
```

Then run:

```
python - <<'PY'
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://localstack:4566",
    region_name="eu-west-2",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

print(s3.list_buckets())
PY
```

If you get:

```
'Buckets': []
```

then no buckets exist.



### 2. Create Bucket Manually

python - <<'PY'
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://localstack:4566",
    region_name="eu-west-2",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

s3.create_bucket(
    Bucket="bp-submission-files",
    CreateBucketConfiguration={
        "LocationConstraint": "eu-west-2"
    }
)

print("Bucket created")
PY



### 3. Create it automatically

Since you're already creating DynamoDB tables, it's a good idea to create the S3 bucket at startup too. You can use:

- A Kubernetes `Job`.
- A LocalStack initialization script.
- An application startup routine (for development only).

Example:

```
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client(
    "s3",
    endpoint_url="http://localstack:4566",
    region_name="eu-west-2",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

bucket = "my-bucket"

try:
    s3.head_bucket(Bucket=bucket)
except ClientError:
    s3.create_bucket(Bucket=bucket)
```

This makes the bucket available automatically if it doesn't already exist.



### Option 2: Kubernetes Job

If you don't want to mount scripts into LocalStack, create a `Job` that waits for LocalStack and initializes resources.

Example:

```
apiVersion: batch/v1
kind: Job
metadata:
  name: localstack-init
  namespace: bp-bedrock
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: init
        image: localstack/localstack:3.0.2
        command:
        - sh
        - -c
        - |
          until curl -s http://localstack:4566/_localstack/health > /dev/null; do
            echo "Waiting for LocalStack..."
            sleep 2
          done

          echo "Creating DynamoDB table..."
          aws dynamodb create-table \
            --table-name bp-submissions \
            --attribute-definitions AttributeName=id,AttributeType=S \
            --key-schema AttributeName=id,KeyType=HASH \
            --billing-mode PAY_PER_REQUEST \
            --endpoint-url http://localstack:4566 \
            --region eu-west-2

          echo "Creating S3 bucket..."  
          awslocal s3api create-bucket \
            --bucket bp-submissions-files \
             --region eu-west-2 || true

          echo "Creating SQS queue..."
          awslocal sqs create-queue \
            --queue-name bp-submission-conversion-queue \
            --region eu-west-2 || true
```



Apply after the LocalStack deployment:

```
kubectl apply -f localstack-deployment.yaml
kubectl apply -f localstack-init.yaml
```



# ERROR 7: QueueDoesNotExist



QS_QUEUE_NAME=bp-submission-conversion-queue











# Acccess the Application on Kubernetes



Frontend

​	http://localhost/



Backend Docs

​	http://localhost/docs



​	curl http://localhost/api/openapi.json 

{"openapi":"3.1.0","info":{"title":"BP Bedrock Submission Service



## Connection to DocumentDB on localstack



Connection String - "mongodb://username:password@documentdb-cluster.cluster-xxxx.eu-west-2.docdb.amazonaws.com:27017/"

​      \- DYNAMODB_SUBMISSIONS_TABLE=bp-submissions

​      \- DYNAMODB_USERS_TABLE=bp-users



## Using the AWS CLI

```
aws dynamodb list-tables \
  --endpoint-url=http://localhost:4566 \
  --region eu-west-2
```



If you're running inside the cluster:

```
aws dynamodb list-tables \
  --endpoint-url=http://localstack:4566 \
  --region eu-west-2
```



Remember to set credentials (dummy values are fine for LocalStack):

```
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
```



## Inside the LocalStack container:

```
kubectl exec -it deployment/localstack -n bp-bedrock -- bash
```

Then:

```
awslocal dynamodb list-tables
```

Describe a table:

```
awslocal dynamodb describe-table \
    --table-name bp-submissions
```

Scan the table:

```
awslocal dynamodb scan \
    --table-name bp-submissions
```

Get an item:

```
awslocal dynamodb get-item \
    --table-name bp-submissions \
    --key '{"id":{"S":"123"}}'
```



## Verify it can reach LocalStack

Because your LocalStack is running inside Kubernetes, make sure port `4566` is exposed to your Mac:

```
kubectl port-forward service/localstack 4566:4566 -n bp-bedrock
```

Keep that terminal running.

Then your DynamoDB Admin container can connect through:

```
http://host.docker.internal:4566
```

Test:

```
curl http://localhost:4566/_localstack/health
```

You should see LocalStack services including DynamoDB.

Then refresh:

```
http://localhost:8001
```

You should see your DynamoDB tables such as:

```
bp-submissions
```



## Option 1: Run DynamoDB Admin with Docker (recommended)

Since you already use Docker, run:

```
docker run -d \
  --name dynamodb-admin \
  -p 8001:8001 \
  -e DYNAMO_ENDPOINT=http://host.docker.internal:4566 \
  aaronshaf/dynamodb-admin
```

Open:

```
http://localhost:8001
```



## Option 2: Run DynamoDB Admin inside Kubernetes

Create dynamodb-admin.yaml:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dynamodb-admin
  namespace: bp-bedrock
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dynamodb-admin
  template:
    metadata:
      labels:
        app: dynamodb-admin
    spec:
      containers:
      - name: dynamodb-admin
        image: aaronshaf/dynamodb-admin
        ports:
        - containerPort: 8001
        env:
        - name: DYNAMO_ENDPOINT
          value: http://localstack:4566
        - name: AWS_REGION
          value: eu-west-2
---
apiVersion: v1
kind: Service
metadata:
  name: dynamodb-admin
  namespace: bp-bedrock
spec:
  selector:
    app: dynamodb-admin
  ports:
  - port: 8001
    targetPort: 8001
```

Apply:

```
kubectl apply -f dynamodb-admin.yaml
```

Access:

```
kubectl port-forward service/dynamodb-admin 8001:8001 -n bp-bedrock
```

Open:

```
http://localhost:8001
```





## Kubernetes  Application Flow



Frontend
   |
   v
NGINX
   |
   v
FastAPI backend
   |
   v
LocalStack DynamoDB  ✅ connected
   |
   v
bp-submissions table ❌ missing