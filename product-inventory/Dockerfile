# Use Node.js for both build and serve
FROM node:20-alpine

WORKDIR /app

# Copy package.json first for caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy rest of the app
COPY . .

# Build the app
RUN npm run build

# Expose port for Vite preview server
EXPOSE 4173

# Run Vite preview (serves from /dist)
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"]
