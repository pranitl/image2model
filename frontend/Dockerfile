# Multi-stage build for React frontend
FROM node:18-alpine as base

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.npm \
    npm install --only=production && npm cache clean --force

# Development stage
FROM node:18-alpine as development

# Set environment variables
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV FAST_REFRESH=true

# Install development tools
RUN apk add --no-cache git

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
RUN --mount=type=cache,target=/root/.npm \
    npm install && npm cache clean --force

# Copy source code
COPY . .

# Expose development server port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Production build stage
FROM base as builder

# Set environment
ENV NODE_ENV=production

# Copy source code
COPY . .

# Install dev dependencies needed for build
RUN --mount=type=cache,target=/root/.npm \
    npm install

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production

# Copy custom nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80 || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]