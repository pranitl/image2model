# Dockerfile for Simple Frontend - Static HTML/CSS/JS
FROM nginx:alpine

# Install curl for healthcheck
RUN apk add --no-cache curl

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy nginx configuration
COPY docker/nginx-simple.conf /etc/nginx/conf.d/default.conf

# Copy static files to nginx html directory
COPY . /usr/share/nginx/html/

# Remove Dockerfile and other non-web files from served directory
RUN rm -f /usr/share/nginx/html/Dockerfile \
    /usr/share/nginx/html/docker/nginx-simple.conf \
    /usr/share/nginx/html/*.md \
    /usr/share/nginx/html/test-*.html

# Create a simple 404 page
RUN echo '<!DOCTYPE html><html><head><title>404 Not Found</title><link rel="stylesheet" href="/css/style.css"></head><body><div class="container"><h1>404 - Page Not Found</h1><p>The page you are looking for does not exist.</p><a href="/" class="btn-primary">Go Home</a></div></body></html>' > /usr/share/nginx/html/404.html

# Create a simple 50x error page
RUN echo '<!DOCTYPE html><html><head><title>Server Error</title><link rel="stylesheet" href="/css/style.css"></head><body><div class="container"><h1>Server Error</h1><p>Something went wrong. Please try again later.</p><a href="/" class="btn-primary">Go Home</a></div></body></html>' > /usr/share/nginx/html/50x.html

# Set proper permissions
RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Expose port 80
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]