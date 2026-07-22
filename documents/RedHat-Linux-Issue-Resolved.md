Issue

    Unable to PutItem in dynamoDB from backend, while creating a new 
    Frontend first screen throws error

Core Resolution

    Inside docker, while making connection to aws (dynamodb) backend uses localstack and NOT localhost (see docker-compose.yml)
        AWS_ENDPOINT_URL=http://localstack:4566
    

    Proxy in corporate networks was causing issue for not allowing localstack to be connected.

    Make the following changes in docker-compose.yml file to include localstack as no_proxy while configuring docker container "backend" in docker-compose.yml

        no_proxy=localhost,127.0.0.1.......,localstack
        NO_PROXY=localhost,127.0.0.1.......,localstack
        HTTP_PROXY=http://1.2.3.4:8080
        HTTPS_PROXY=http://4.3.2.1:8080

NOTE : Outside docker, aws can still be accessed thru localhost but inside docker it points to backend itself and not localstack.

Misc Other commands

    To check what is proxy configured in your development environment

        env | grep -i proxy

    To check if backend has included localstack as no_proxy

        docker exec -it <backend-container> env | grep -i proxy
    
    To check if Docker itself uses a proxy:

        systemctl show --property=Environment docker
    or:
        cat /etc/systemd/system/docker.service.d/http-proxy.conf

    To get inside into your docker container, say backend
    
        docker exec -it <backend-container> sh



