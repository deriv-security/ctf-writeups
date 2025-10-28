FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY app/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY app/ ./

COPY flag.txt /flag.txt

# Expose port
EXPOSE 3001

# Start the application
CMD ["npm", "start"]
