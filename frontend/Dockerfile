# Relative path: frontend/.env

FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .

ARG VITE_CATALOG_BASE_URL
ARG VITE_CATALOG_SERVER_URL
ENV VITE_CATALOG_BASE_URL=$VITE_CATALOG_BASE_URL
ENV VITE_CATALOG_SERVER_URL=$VITE_CATALOG_SERVER_URL

RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist/client /usr/share/nginx/html

EXPOSE 80
