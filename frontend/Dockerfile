# Build stage
FROM node:25-alpine AS builder

# Accept build arguments for environment variables
ARG VITE_API_BASE_URL=http://localhost:8082
ARG VITE_NODE_ENV=staging
ARG VITE_APP_NAME=ZeroInertia
ARG VITE_APP_VERSION=0.0.1

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy application files
COPY . .

# Build the application (Vite will use ARG values as environment variables)
RUN npm run build

# Runtime stage
FROM nginx:alpine

# Accept build argument for nginx config (prod or staging)
ARG NGINX_CONFIG=nginx.prod.conf

COPY --from=builder /app/dist /usr/share/nginx/html
COPY ${NGINX_CONFIG} /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]