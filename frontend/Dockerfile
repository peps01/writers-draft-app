FROM node:22-slim

WORKDIR /app

RUN npm install -g @quasar/cli

COPY . .
RUN npm install

EXPOSE 9000