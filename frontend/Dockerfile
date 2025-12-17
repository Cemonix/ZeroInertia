# Build stage
FROM node:25-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy application files and .env
COPY . .

# Build the application (Vite will read .env file during build)
RUN npm run build

# Runtime stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY ../nginx.prod.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]