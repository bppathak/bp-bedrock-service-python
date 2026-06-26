version: "3.9"

services:
  localstack:
    image: localstack/localstack:3.0.2
    networks:
      - bp-app-network
    container_name: localstack
    ports:
      - "4566:4566"
    environment:
      - SERVICES=s3,dynamodb,sqs,lambda
      - DEBUG=1
      - AWS_DEFAULT_REGION=eu-west-2
      - AWS_ACCESS_KEY_ID=test
      - AWS_SECRET_ACCESS_KEY=test      
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock

  backend:
    build:
      context: ./backend_python
      dockerfile: Dockerfile
    image: backend-python
    networks:
      - bp-app-network
    container_name: python-backend
    ports:
      - "8000:8000"
  frontend:
    build:
      context: ./frontend_react
      dockerfile: Dockerfile
    image: frontend-react
    networks:
      - bp-app-network
    container_name: react-frontend
    ports:
      - "5173:5173"
      - VITE_API_BASE_URL=http://localhost:8000
    depends_on:
      - backend

networks:
  bp-app-network:
    driver: bridge