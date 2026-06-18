# Build stage
FROM node:20 AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# Production stage
#FROM node:20

#WORKDIR /app

#COPY package*.json ./
#RUN npm install --omit=dev

#COPY --from=builder /frontend_react/.next ./.next
#COPY --from=builder /frontend_react/public ./public
#COPY --from=builder /frontend_react/next.config.* ./

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# CMD ["npm", "start"]
