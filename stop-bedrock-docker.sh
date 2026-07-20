docker compose down
sleep 5
docker rmi -f $(docker images -aq)