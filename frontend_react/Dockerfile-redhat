# Build stage
FROM node:20 AS builder

WORKDIR /frontend_react

COPY package*.json ./
RUN npm install
# Production stage
#FROM node:20

#WORKDIR /frontend_react

#COPY package*.json ./
#RUN npm install --omit=dev

EXPOSE 5173

CMD ["npm", "start"]