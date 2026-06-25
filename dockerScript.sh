docker network inspect bp-bedrock-service-python_bp-app-network

docker exec -it backend sh
echo $AWS_ENDPOINT

Get insided python-backend & look at localstack 

    dockedr exec -i python-backend sh
    getent hosts localstack
    curl http://localstack:4566/_localstack/health

docker network ls

docker inspect localstack --format='{{json .NetworkSettings.Networks}}'
docker inspect bedrock-localstack --format='{{json .NetworkSettings.Networks}}'

docker inspect python-backend --format='{{json .NetworkSettings.Networks}}'
