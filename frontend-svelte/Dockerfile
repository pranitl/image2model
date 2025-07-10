# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Accept PUBLIC_API_URL as build argument
ARG PUBLIC_API_URL

# Set PUBLIC_API_URL environment variable for build process
ENV PUBLIC_API_URL=$PUBLIC_API_URL

# Don't set API_KEY at build time since we're using dynamic env
# Build the app
RUN npm run build

# Production stage
FROM node:20-alpine AS production

WORKDIR /app

# Copy built app from builder stage
COPY --from=builder /app/build ./build
COPY --from=builder /app/package*.json ./

# Install only production dependencies
RUN npm ci --omit=dev

# Expose port 3000
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

# IMPORTANT: API_KEY will be provided at runtime via docker-compose or env
# The app needs to read it from process.env at runtime, not build time

# Run the app
CMD ["node", "build"]
