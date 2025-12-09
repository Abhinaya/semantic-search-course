# Frontend Dockerfile - serves static files with npx serve
FROM node:20-alpine

WORKDIR /app

# Copy frontend files
COPY index.html .

# Expose port
EXPOSE 3000

# Run with npx serve (no installation needed)
CMD ["npx", "serve", ".", "-l", "3000"]
