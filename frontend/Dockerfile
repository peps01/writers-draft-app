FROM node:22-slim

WORKDIR /app

RUN npm install -g @quasar/cli

COPY . .
RUN npm install --legacy-peer-deps

EXPOSE 9000