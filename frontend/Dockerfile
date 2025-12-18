# Build stage
FROM node:25-alpine AS builder

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